"""Authentication routes with DB-backed sessions and user-owned data APIs."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import secrets
import tempfile
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..cv_extractor import CVExtractor
from ..cv_section_parser import CVSectionParser
from ..keyword_extractor import KeywordExtractor
from ..keyword_placement_agent import ImprovedCVSections
from ..keyword_rating_agent import KeywordRatingAgent
from ..latex_cv_generator import LaTeXCVGenerator
from ..pdf_generator import PDFGenerator
from ..skill_extractor import SkillExtractor
from ..skill_merge import join_skills_csv, merge_unique_skills
from .auth_schemas import (
    AuthResponse,
    CVEnhanceGenerateRequest,
    CVEnhanceGenerateResponse,
    CVUploadRequest,
    CVWorkspaceCertificationEntry,
    CVWorkspaceEducationEntry,
    CVWorkspacePersonalInfo,
    CVWorkspaceProjectEntry,
    CVWorkspaceResponse,
    CVWorkspaceSections,
    CVWorkspaceUpdateRequest,
    CVWorkspaceWorkExperienceEntry,
    JDKeywordAnalysisRequest,
    JDKeywordAnalysisResponse,
    LoginRequest,
    MessageResponse,
    SignupRequest,
    UserDataCreateRequest,
    UserDataListResponse,
    UserDataResponse,
    UserDataUpdateRequest,
    UserJobItemCreateRequest,
    UserJobItemResponse,
    UserJobItemUpdate,
    UserJobListResponse,
    UserJobListUpdateRequest,
    UserResponse,
)
from .db import get_db
from .db_models import User, UserCvWorkspace, UserDataItem, UserJobItem, UserSession

auth_router = APIRouter(prefix="/api/v1", tags=["Auth"])

PASSWORD_HASH_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "600000"))
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "ats_session")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower()
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")
ALLOWED_JOB_STATUSES = {"Applied", "Interview", "Rejected"}

if SESSION_COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    SESSION_COOKIE_SAMESITE = "lax"


def _normalize_email(raw_email: str) -> str:
    return raw_email.strip().lower()


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return "pbkdf2_sha256${iterations}${salt}${digest}".format(
        iterations=PASSWORD_HASH_ITERATIONS,
        salt=base64.b64encode(salt).decode("ascii"),
        digest=base64.b64encode(derived_key).decode("ascii"),
    )


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, raw_iterations, raw_salt, raw_digest = stored_hash.split("$", maxsplit=3)
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(raw_iterations)
        salt = base64.b64decode(raw_salt.encode("ascii"))
        expected_digest = base64.b64decode(raw_digest.encode("ascii"))
    except (ValueError, TypeError):
        return False

    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(candidate_digest, expected_digest)


def _hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _set_session_cookie(response: Response, token: str) -> None:
    cookie_kwargs: dict[str, object] = {
        "httponly": True,
        "secure": SESSION_COOKIE_SECURE,
        "samesite": SESSION_COOKIE_SAMESITE,
        "max_age": SESSION_TTL_HOURS * 3600,
        "path": "/",
    }

    if SESSION_COOKIE_DOMAIN:
        cookie_kwargs["domain"] = SESSION_COOKIE_DOMAIN

    response.set_cookie(SESSION_COOKIE_NAME, token, **cookie_kwargs)


def _delete_session_cookie(response: Response) -> None:
    cookie_kwargs: dict[str, object] = {"path": "/"}
    if SESSION_COOKIE_DOMAIN:
        cookie_kwargs["domain"] = SESSION_COOKIE_DOMAIN
    response.delete_cookie(SESSION_COOKIE_NAME, **cookie_kwargs)


def _create_session(db: Session, user_id: int, request: Request) -> str:
    raw_token = secrets.token_urlsafe(48)
    now = datetime.utcnow()

    session = UserSession(
        user_id=user_id,
        token_hash=_hash_session_token(raw_token),
        created_at=now,
        expires_at=now + timedelta(hours=SESSION_TTL_HOURS),
        user_agent=(request.headers.get("user-agent") or "")[:512],
        ip_address=request.client.host if request.client else None,
    )
    db.add(session)
    db.commit()
    return raw_token


def _get_valid_session(db: Session, token: str) -> UserSession | None:
    now = datetime.utcnow()
    query = select(UserSession).where(
        UserSession.token_hash == _hash_session_token(token),
        UserSession.revoked_at.is_(None),
        UserSession.expires_at > now,
    )
    return db.execute(query).scalar_one_or_none()


def _get_workspace(db: Session, user_id: int) -> UserCvWorkspace | None:
    query = select(UserCvWorkspace).where(UserCvWorkspace.user_id == user_id)
    return db.execute(query).scalar_one_or_none()


def _split_blocks(text: str) -> list[str]:
    return [block.strip() for block in (text or "").split("\n\n") if block.strip()]


def _normalize_personal_info(raw: Any) -> CVWorkspacePersonalInfo:
    if isinstance(raw, CVWorkspacePersonalInfo):
        return raw

    if isinstance(raw, str):
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        name = lines[0] if lines else ""
        return CVWorkspacePersonalInfo(name=name)

    if isinstance(raw, dict):
        return CVWorkspacePersonalInfo(
            name=str(raw.get("name", "") or "").strip(),
            phone=str(raw.get("phone", "") or "").strip(),
            email=str(raw.get("email", "") or "").strip(),
            location=str(raw.get("location", "") or "").strip(),
        )

    return CVWorkspacePersonalInfo()


def _normalize_work_experience_entries(raw: Any) -> list[CVWorkspaceWorkExperienceEntry]:
    if isinstance(raw, list):
        normalized: list[CVWorkspaceWorkExperienceEntry] = []
        for item in raw:
            if isinstance(item, dict):
                if "title" in item and "content" in item:
                    normalized.append(
                        CVWorkspaceWorkExperienceEntry(
                            company_name=str(item.get("title", "") or "").strip(),
                            overview=str(item.get("content", "") or "").strip(),
                        )
                    )
                else:
                    normalized.append(
                        CVWorkspaceWorkExperienceEntry(
                            company_name=str(item.get("company_name", "") or "").strip(),
                            location=str(item.get("location", "") or "").strip(),
                            role=str(item.get("role", "") or "").strip(),
                            start_date=str(item.get("start_date", "") or "").strip(),
                            end_date=str(item.get("end_date", "") or "").strip(),
                            currently_working=bool(item.get("currently_working", False)),
                            overview=str(item.get("overview", item.get("details", "")) or "").strip(),
                        )
                    )
        return [entry for entry in normalized if any(entry.model_dump().values())]

    if isinstance(raw, dict):
        return _normalize_work_experience_entries(raw.get("entries", []))

    if isinstance(raw, str):
        entries: list[CVWorkspaceWorkExperienceEntry] = []
        for block in _split_blocks(raw):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            entries.append(
                CVWorkspaceWorkExperienceEntry(
                    company_name=lines[0],
                    role=lines[1] if len(lines) > 1 else "",
                    overview="\n".join(lines[2:]).strip() if len(lines) > 2 else "\n".join(lines[1:]).strip(),
                    currently_working="present" in block.lower() or "current" in block.lower(),
                )
            )
        return entries

    return []


def _normalize_education_entries(raw: Any) -> list[CVWorkspaceEducationEntry]:
    if isinstance(raw, list):
        normalized: list[CVWorkspaceEducationEntry] = []
        for item in raw:
            if isinstance(item, dict):
                if "title" in item and "content" in item:
                    normalized.append(
                        CVWorkspaceEducationEntry(
                            institution_name=str(item.get("title", "") or "").strip(),
                            overview=str(item.get("content", "") or "").strip(),
                        )
                    )
                else:
                    normalized.append(
                        CVWorkspaceEducationEntry(
                            institution_name=str(item.get("institution_name", item.get("school", "")) or "").strip(),
                            location=str(item.get("location", "") or "").strip(),
                            degree=str(item.get("degree", "") or "").strip(),
                            start_date=str(item.get("start_date", "") or "").strip(),
                            end_date=str(item.get("end_date", "") or "").strip(),
                            currently_studying=bool(item.get("currently_studying", False)),
                            overview=str(item.get("overview", item.get("details", "")) or "").strip(),
                        )
                    )
        return [entry for entry in normalized if any(entry.model_dump().values())]

    if isinstance(raw, dict):
        return _normalize_education_entries(raw.get("entries", []))

    if isinstance(raw, str):
        entries: list[CVWorkspaceEducationEntry] = []
        for block in _split_blocks(raw):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            entries.append(
                CVWorkspaceEducationEntry(
                    institution_name=lines[0],
                    degree=lines[1] if len(lines) > 1 else "",
                    overview="\n".join(lines[2:]).strip() if len(lines) > 2 else "\n".join(lines[1:]).strip(),
                    currently_studying="present" in block.lower() or "current" in block.lower(),
                )
            )
        return entries

    return []


def _normalize_project_entries(raw: Any) -> list[CVWorkspaceProjectEntry]:
    if isinstance(raw, list):
        normalized: list[CVWorkspaceProjectEntry] = []
        for item in raw:
            if isinstance(item, dict):
                if "title" in item and "content" in item:
                    normalized.append(
                        CVWorkspaceProjectEntry(
                            project_name=str(item.get("title", "") or "").strip(),
                            details=str(item.get("content", "") or "").strip(),
                        )
                    )
                else:
                    normalized.append(
                        CVWorkspaceProjectEntry(
                            project_name=str(item.get("project_name", item.get("name", "")) or "").strip(),
                            details=str(item.get("details", item.get("overview", "")) or "").strip(),
                        )
                    )
        return [entry for entry in normalized if entry.project_name or entry.details]

    if isinstance(raw, dict):
        return _normalize_project_entries(raw.get("entries", []))

    if isinstance(raw, str):
        entries: list[CVWorkspaceProjectEntry] = []
        for block in _split_blocks(raw):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            entries.append(
                CVWorkspaceProjectEntry(
                    project_name=lines[0],
                    details="\n".join(lines[1:]).strip() if len(lines) > 1 else block,
                )
            )
        return entries

    return []


def _normalize_certification_entries(raw: Any) -> list[CVWorkspaceCertificationEntry]:
    if isinstance(raw, list):
        normalized: list[CVWorkspaceCertificationEntry] = []
        for item in raw:
            if isinstance(item, dict):
                if "title" in item and "content" in item:
                    normalized.append(
                        CVWorkspaceCertificationEntry(
                            certification_name=str(item.get("title", "") or "").strip(),
                            details=str(item.get("content", "") or "").strip(),
                        )
                    )
                else:
                    normalized.append(
                        CVWorkspaceCertificationEntry(
                            certification_name=str(item.get("certification_name", item.get("name", "")) or "").strip(),
                            details=str(item.get("details", item.get("overview", "")) or "").strip(),
                        )
                    )
        return [entry for entry in normalized if entry.certification_name or entry.details]

    if isinstance(raw, dict):
        return _normalize_certification_entries(raw.get("entries", []))

    if isinstance(raw, str):
        entries: list[CVWorkspaceCertificationEntry] = []
        for block in _split_blocks(raw):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue
            entries.append(
                CVWorkspaceCertificationEntry(
                    certification_name=lines[0],
                    details="\n".join(lines[1:]).strip() if len(lines) > 1 else "",
                )
            )
        return entries

    return []


def _normalize_sections(raw_sections: Any) -> CVWorkspaceSections:
    if isinstance(raw_sections, CVWorkspaceSections):
        return raw_sections

    if not isinstance(raw_sections, dict):
        return CVWorkspaceSections()

    return CVWorkspaceSections(
        personal_info=_normalize_personal_info(raw_sections.get("personal_info")),
        professional_summary_overview=str(
            raw_sections.get("professional_summary_overview", raw_sections.get("professional_summary", "")) or ""
        ).strip(),
        skills_overview=str(raw_sections.get("skills_overview", raw_sections.get("skills", "")) or "").strip(),
        work_experience=_normalize_work_experience_entries(raw_sections.get("work_experience", [])),
        education=_normalize_education_entries(raw_sections.get("education", [])),
        projects=_normalize_project_entries(raw_sections.get("projects", [])),
        certifications=_normalize_certification_entries(raw_sections.get("certifications", [])),
        additional_overview=str(raw_sections.get("additional_overview", raw_sections.get("additional", "")) or "").strip(),
    )


def _extract_job_targets(job_description: str) -> tuple[str, str, list[str]]:
    """
    Extract company name, position, and JD skills for CV enhancement.
    Falls back to keyword extraction if structured extraction fails.
    """
    company_name = ""
    position = ""

    try:
        skill_extractor = SkillExtractor()
        target_data = skill_extractor.extract_target_cv_data_from_job_description(job_description)
        candidates = target_data.skills
        company_name = target_data.company_name.strip()
        position = target_data.position.strip()
    except Exception:
        extractor = KeywordExtractor(use_spacy=False)
        extracted_keywords = extractor.extract_keywords(job_description, max_keywords=80)
        try:
            rating_agent = KeywordRatingAgent()
            rated = rating_agent.rate_keywords(extracted_keywords, job_description)
            candidates = [*rated.get("required", []), *rated.get("optional", [])]
        except Exception:
            candidates = extracted_keywords
        candidates = SkillExtractor._sanitize_for_cv_skills(candidates)

    unique_keywords: list[str] = []
    seen: set[str] = set()
    for keyword in candidates:
        cleaned = str(keyword or "").strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_keywords.append(cleaned)

    return company_name, position, unique_keywords[:40]


def _normalize_job_status(raw_status: str | None) -> str:
    status_value = str(raw_status or "").strip().title()
    if status_value not in ALLOWED_JOB_STATUSES:
        return "Applied"
    return status_value


def _job_item_response(item: UserJobItem) -> UserJobItemResponse:
    return UserJobItemResponse.model_validate(item)


def _job_items_query(db: Session, user_id: int):
    return (
        select(UserJobItem)
        .where(UserJobItem.user_id == user_id)
        .order_by(UserJobItem.sort_order.asc(), UserJobItem.id.asc())
    )


def _has_workspace_content(sections: CVWorkspaceSections) -> bool:
    return any(
        [
            any(sections.personal_info.model_dump().values()),
            bool(sections.professional_summary_overview.strip()),
            bool(sections.skills_overview.strip()),
            any(any(entry.model_dump().values()) for entry in sections.work_experience),
            any(any(entry.model_dump().values()) for entry in sections.education),
            any(entry.project_name or entry.details for entry in sections.projects),
            any(entry.certification_name or entry.details for entry in sections.certifications),
            bool(sections.additional_overview.strip()),
        ]
    )


def _format_work_experience_for_latex(entries: list[CVWorkspaceWorkExperienceEntry]) -> str:
    blocks: list[str] = []
    for entry in entries:
        if not any(entry.model_dump().values()):
            continue

        role = entry.role.strip() or "Work Experience"
        company = entry.company_name.strip() or "Company"
        if entry.location.strip():
            company = f"{company}, {entry.location.strip()}"

        end_value = "Present" if entry.currently_working else entry.end_date.strip()
        date_range = " - ".join([part for part in [entry.start_date.strip(), end_value] if part])

        lines = [role]
        lines.append(f"{company} | {date_range}" if date_range else company)
        for overview_line in [line.strip() for line in entry.overview.splitlines() if line.strip()]:
            lines.append(f"- {overview_line}")
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks).strip()


def _format_education_for_latex(entries: list[CVWorkspaceEducationEntry]) -> str:
    blocks: list[str] = []
    for entry in entries:
        if not any(entry.model_dump().values()):
            continue

        degree = entry.degree.strip() or "Education"
        institution = entry.institution_name.strip() or "Institution"
        if entry.location.strip():
            institution = f"{institution}, {entry.location.strip()}"

        end_value = "Present" if entry.currently_studying else entry.end_date.strip()
        date_range = " - ".join([part for part in [entry.start_date.strip(), end_value] if part])

        lines = [degree]
        lines.append(f"{institution} | {date_range}" if date_range else institution)
        for overview_line in [line.strip() for line in entry.overview.splitlines() if line.strip()]:
            lines.append(overview_line)
        blocks.append("\n".join(lines))

    return "\n\n".join(blocks).strip()


def _format_projects_for_latex(entries: list[CVWorkspaceProjectEntry]) -> str:
    lines: list[str] = []
    for entry in entries:
        if not entry.project_name and not entry.details:
            continue
        title = entry.project_name.strip() or "Project"
        details = entry.details.strip()
        lines.append(f"- {title}: {details}" if details else f"- {title}")
    return "\n".join(lines).strip()


def _format_certifications_for_latex(entries: list[CVWorkspaceCertificationEntry]) -> str:
    lines: list[str] = []
    for entry in entries:
        if not entry.certification_name and not entry.details:
            continue
        title = entry.certification_name.strip() or "Certification"
        details = entry.details.strip()
        lines.append(f"- {title}: {details}" if details else f"- {title}")
    return "\n".join(lines).strip()


def _workspace_sections_to_improved_sections(sections: CVWorkspaceSections) -> ImprovedCVSections:
    personal_lines: list[str] = []
    if sections.personal_info.name.strip():
        personal_lines.append(sections.personal_info.name.strip())
    if sections.personal_info.email.strip():
        personal_lines.append(f"Email: {sections.personal_info.email.strip()}")
    if sections.personal_info.phone.strip():
        personal_lines.append(f"Phone: {sections.personal_info.phone.strip()}")
    if sections.personal_info.location.strip():
        personal_lines.append(f"Location: {sections.personal_info.location.strip()}")

    personal_info = "\n".join(personal_lines).strip()

    return ImprovedCVSections(
        personal_info=personal_info or "Your Name",
        professional_summary=sections.professional_summary_overview.strip(),
        skills=sections.skills_overview.strip(),
        work_experience=_format_work_experience_for_latex(sections.work_experience),
        education=_format_education_for_latex(sections.education),
        projects=_format_projects_for_latex(sections.projects),
        certifications=_format_certifications_for_latex(sections.certifications),
        additional=sections.additional_overview.strip(),
        placement_notes="Generated from My Data workspace and merged JD keywords.",
    )


def _workspace_response(workspace: UserCvWorkspace | None) -> CVWorkspaceResponse:
    if not workspace:
        return CVWorkspaceResponse(
            has_uploaded_cv=False,
            cv_file_name=None,
            sections=CVWorkspaceSections(),
            updated_at=None,
        )

    try:
        raw_sections = json.loads(workspace.sections_json or "{}")
    except json.JSONDecodeError:
        raw_sections = {}

    normalized_sections = _normalize_sections(raw_sections)

    return CVWorkspaceResponse(
        has_uploaded_cv=workspace.has_uploaded_cv,
        cv_file_name=workspace.cv_file_name,
        sections=normalized_sections,
        updated_at=workspace.updated_at,
    )


def _upsert_workspace(db: Session, user_id: int) -> UserCvWorkspace:
    workspace = _get_workspace(db, user_id)
    if workspace:
        return workspace

    workspace = UserCvWorkspace(user_id=user_id, sections_json="{}")
    db.add(workspace)
    db.flush()
    return workspace


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    active_session = _get_valid_session(db, token)
    if not active_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    user = db.get(User, active_session.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session user")

    return user


@auth_router.post("/auth/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: SignupRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = _normalize_email(payload.email)
    first_name = payload.first_name.strip()

    if "@" not in email or "." not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    if not first_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="First name is required")

    existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(first_name=first_name, email=email, password_hash=_hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = _create_session(db, user.id, request)
    _set_session_cookie(response, token)

    return AuthResponse(message="User created", user=UserResponse.model_validate(user))


@auth_router.post("/auth/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email = _normalize_email(payload.email)
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = _create_session(db, user.id, request)
    _set_session_cookie(response, token)

    return AuthResponse(message="Login successful", user=UserResponse.model_validate(user))


@auth_router.post("/auth/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        active_session = _get_valid_session(db, token)
        if active_session:
            active_session.revoked_at = datetime.utcnow()
            db.commit()

    _delete_session_cookie(response)
    return MessageResponse(message="Logout successful")


@auth_router.get("/auth/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@auth_router.get("/cv/workspace", response_model=CVWorkspaceResponse)
def get_cv_workspace(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = _get_workspace(db, current_user.id)
    return _workspace_response(workspace)


@auth_router.post("/cv/enhance/analyze-jd", response_model=JDKeywordAnalysisResponse)
def analyze_job_description_keywords(
    payload: JDKeywordAnalysisRequest,
    current_user: User = Depends(get_current_user),  # noqa: ARG001
):
    company_name, position, keywords = _extract_job_targets(payload.job_description)
    return JDKeywordAnalysisResponse(
        keywords=keywords,
        keywords_csv=", ".join(keywords),
        company_name=company_name,
        position=position,
    )


@auth_router.post("/cv/enhance/generate-pdf", response_model=CVEnhanceGenerateResponse)
def generate_enhanced_cv_pdf(
    payload: CVEnhanceGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keywords = [str(keyword or "").strip() for keyword in payload.keywords if str(keyword or "").strip()]
    if not keywords:
        _, _, keywords = _extract_job_targets(payload.job_description)

    workspace = _upsert_workspace(db, current_user.id)
    try:
        raw_sections = json.loads(workspace.sections_json or "{}")
    except json.JSONDecodeError:
        raw_sections = {}

    normalized_sections = _normalize_sections(raw_sections)
    if not _has_workspace_content(normalized_sections):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="My Data is empty. Upload your CV or add your data first.",
        )

    merged_skills = merge_unique_skills(normalized_sections.skills_overview, keywords)
    normalized_sections.skills_overview = join_skills_csv(merged_skills)

    workspace.sections_json = json.dumps(normalized_sections.model_dump())
    db.commit()
    db.refresh(workspace)

    if not PDFGenerator.check_latex_installed():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="pdflatex is not installed. Install LaTeX to generate PDF output.",
        )

    improved_sections = _workspace_sections_to_improved_sections(normalized_sections)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tex_path = os.path.join(temp_dir, "enhanced_cv.tex")
            latex_code = LaTeXCVGenerator.generate_latex(improved_sections)

            with open(tex_path, "w", encoding="utf-8") as tex_file:
                tex_file.write(latex_code)

            pdf_path = PDFGenerator.compile_latex_to_pdf(tex_path, temp_dir)
            with open(pdf_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate enhanced CV PDF: {exc}",
        ) from exc

    return CVEnhanceGenerateResponse(
        keywords_used=keywords,
        merged_skills_overview=normalized_sections.skills_overview,
        pdf_base64=pdf_base64,
        pdf_file_name="enhanced_cv.pdf",
    )


@auth_router.post("/cv/workspace/upload", response_model=CVWorkspaceResponse)
def upload_cv_and_extract_sections(
    payload: CVUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    temp_pdf_path: str | None = None

    try:
        cv_bytes = base64.b64decode(payload.cv_base64, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid base64 CV payload")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(cv_bytes)
            temp_pdf.flush()
            temp_pdf_path = temp_pdf.name

        cv_text = CVExtractor.extract_from_pdf(temp_pdf_path)

        parser = CVSectionParser()
        parsed_sections = parser.parse_cv_for_workspace(cv_text)

        workspace = _upsert_workspace(db, current_user.id)
        workspace.cv_file_name = payload.file_name.strip()
        workspace.cv_text = cv_text
        workspace.has_uploaded_cv = True
        workspace.sections_json = json.dumps(parsed_sections.model_dump())

        db.commit()
        db.refresh(workspace)

        return _workspace_response(workspace)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not process CV: {exc}",
        )
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


@auth_router.put("/cv/workspace", response_model=CVWorkspaceResponse)
def update_cv_workspace_sections(
    payload: CVWorkspaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    normalized_sections = _normalize_sections(payload.sections.model_dump())

    workspace = _upsert_workspace(db, current_user.id)
    workspace.sections_json = json.dumps(normalized_sections.model_dump())

    db.commit()
    db.refresh(workspace)

    return _workspace_response(workspace)


@auth_router.post("/cv/workspace/reset", response_model=CVWorkspaceResponse)
def reset_cv_workspace(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspace = _upsert_workspace(db, current_user.id)
    workspace.cv_file_name = None
    workspace.cv_text = None
    workspace.has_uploaded_cv = False
    workspace.sections_json = json.dumps(CVWorkspaceSections().model_dump())

    db.commit()
    db.refresh(workspace)

    return _workspace_response(workspace)


@auth_router.get("/jobs", response_model=UserJobListResponse)
def list_user_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = db.execute(_job_items_query(db, current_user.id)).scalars().all()
    return UserJobListResponse(items=[_job_item_response(item) for item in items])


@auth_router.put("/jobs", response_model=UserJobListResponse)
def upsert_user_jobs(
    payload: UserJobListUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_items = db.execute(_job_items_query(db, current_user.id)).scalars().all()
    existing_by_id = {item.id: item for item in existing_items}

    for item in payload.items:
        if item.id is not None and item.id not in existing_by_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job row {item.id} not found")

    kept_ids: set[int] = set()
    sort_order = 0

    for row in payload.items:
        application_date = str(row.application_date or "").strip()
        company_name = str(row.company_name or "").strip()
        position = str(row.position or "").strip()
        status_value = _normalize_job_status(row.status)

        if not any([application_date, company_name, position]):
            continue

        if row.id is not None:
            item = existing_by_id[row.id]
        else:
            item = UserJobItem(user_id=current_user.id)
            db.add(item)
            db.flush()

        item.application_date = application_date
        item.company_name = company_name
        item.position = position
        item.status = status_value
        item.sort_order = sort_order
        sort_order += 1

        if item.id is not None:
            kept_ids.add(item.id)

    for item in existing_items:
        if item.id not in kept_ids:
            db.delete(item)

    db.commit()

    refreshed_items = db.execute(_job_items_query(db, current_user.id)).scalars().all()
    return UserJobListResponse(items=[_job_item_response(item) for item in refreshed_items])


@auth_router.post("/jobs/add-from-jd", response_model=UserJobItemResponse, status_code=status.HTTP_201_CREATED)
def add_job_from_jd(
    payload: UserJobItemCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_name = payload.company_name.strip()
    position = payload.position.strip()

    if not company_name and not position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name or position is required to add a job.",
        )

    application_date = payload.application_date.strip() if payload.application_date else datetime.now().date().isoformat()
    status_value = _normalize_job_status(payload.status or "Applied")

    db.execute(
        update(UserJobItem)
        .where(UserJobItem.user_id == current_user.id)
        .values(sort_order=UserJobItem.sort_order + 1)
    )

    item = UserJobItem(
        user_id=current_user.id,
        application_date=application_date,
        company_name=company_name,
        position=position,
        status=status_value,
        sort_order=0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _job_item_response(item)


@auth_router.post("/me/data", response_model=UserDataResponse, status_code=status.HTTP_201_CREATED)
def create_user_data_item(
    payload: UserDataCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = UserDataItem(
        user_id=current_user.id,
        title=payload.title.strip(),
        content=payload.content.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return UserDataResponse.model_validate(item)


@auth_router.get("/me/data", response_model=UserDataListResponse)
def list_user_data_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(UserDataItem)
        .where(UserDataItem.user_id == current_user.id)
        .order_by(UserDataItem.created_at.desc())
    )
    items = db.execute(query).scalars().all()
    return UserDataListResponse(items=[UserDataResponse.model_validate(item) for item in items])


@auth_router.put("/me/data/{item_id}", response_model=UserDataResponse)
def update_user_data_item(
    item_id: int,
    payload: UserDataUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(UserDataItem).where(
        UserDataItem.id == item_id,
        UserDataItem.user_id == current_user.id,
    )
    item = db.execute(query).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data item not found")

    item.title = payload.title.strip()
    item.content = payload.content.strip()
    db.commit()
    db.refresh(item)
    return UserDataResponse.model_validate(item)


@auth_router.delete("/me/data/{item_id}", response_model=MessageResponse)
def delete_user_data_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(UserDataItem).where(
        UserDataItem.id == item_id,
        UserDataItem.user_id == current_user.id,
    )
    item = db.execute(query).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data item not found")

    db.delete(item)
    db.commit()
    return MessageResponse(message="Data item deleted")
