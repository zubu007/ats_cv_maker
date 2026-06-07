"""Authentication routes with DB-backed sessions and user-owned data APIs."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth_schemas import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    SignupRequest,
    UserDataCreateRequest,
    UserDataListResponse,
    UserDataResponse,
    UserDataUpdateRequest,
    UserResponse,
)
from .db import get_db
from .db_models import User, UserDataItem, UserSession

auth_router = APIRouter(prefix="/api/v1", tags=["Auth"])

PASSWORD_HASH_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "600000"))
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "24"))
SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "ats_session")
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "lax").lower()
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN")

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
    if "@" not in email or "." not in email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

    existing_user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(email=email, password_hash=_hash_password(payload.password))
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
