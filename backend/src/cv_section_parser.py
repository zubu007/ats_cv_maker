"""
CV Section Parser Agent
Parses CV text into structured sections using AI.
"""

import os
import json
import re
from typing import Dict
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv()


class CVSections(BaseModel):
    """Structured CV sections."""

    personal_info: str = Field(description="Name, contact information, email, phone, location")
    professional_summary: str = Field(default="", description="Professional summary or objective statement")
    skills: str = Field(default="", description="Technical skills, programming languages, tools, technologies")
    work_experience: str = Field(description="Work experience, job history, professional experience")
    education: str = Field(description="Education, degrees, certifications, academic background")
    projects: str = Field(default="", description="Personal or professional projects")
    certifications: str = Field(default="", description="Professional certifications and licenses")
    additional: str = Field(default="", description="Any additional sections like awards, publications, volunteer work")


class WorkspacePersonalInfo(BaseModel):
    """Structured personal info fields."""

    name: str = Field(default="")
    phone: str = Field(default="")
    email: str = Field(default="")
    location: str = Field(default="")


class WorkspaceWorkExperienceEntry(BaseModel):
    """One employment entry."""

    company_name: str = Field(default="")
    location: str = Field(default="")
    role: str = Field(default="")
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    currently_working: bool = Field(default=False)
    overview: str = Field(default="")


class WorkspaceEducationEntry(BaseModel):
    """One education entry."""

    institution_name: str = Field(default="")
    location: str = Field(default="")
    degree: str = Field(default="")
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    currently_studying: bool = Field(default=False)
    overview: str = Field(default="")


class WorkspaceProjectEntry(BaseModel):
    """One project entry."""

    project_name: str = Field(default="")
    details: str = Field(default="")


class WorkspaceCertificationEntry(BaseModel):
    """One certification entry."""

    certification_name: str = Field(default="")
    details: str = Field(default="")


class CVWorkspaceSections(BaseModel):
    """Workspace-friendly CV structure with section-specific layouts."""

    personal_info: WorkspacePersonalInfo = Field(default_factory=WorkspacePersonalInfo)
    professional_summary_overview: str = Field(default="")
    skills_overview: str = Field(default="", description="Comma-separated skills")
    work_experience: list[WorkspaceWorkExperienceEntry] = Field(default_factory=list)
    education: list[WorkspaceEducationEntry] = Field(default_factory=list)
    projects: list[WorkspaceProjectEntry] = Field(default_factory=list)
    certifications: list[WorkspaceCertificationEntry] = Field(default_factory=list)
    additional_overview: str = Field(default="")


class CVSectionParser:
    """Parses CV text into structured sections using LangChain."""

    def __init__(self):
        """Initialize the CV section parser."""
        self.provider = os.getenv("AI_PROVIDER", "openai").lower()
        self.model_name = os.getenv("AI_MODEL", "gpt-4-turbo")

        if self.provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif self.provider == "anthropic":
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.1,
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

        # Create structured output parser
        self.structured_llm = self.llm.with_structured_output(CVSections)
        self.workspace_structured_llm = self.llm.with_structured_output(CVWorkspaceSections)

    def parse_cv(self, cv_text: str) -> CVSections:
        """
        Parse CV text into structured sections.

        Args:
            cv_text: Full CV text

        Returns:
            CVSections object with parsed sections
        """
        # Truncate CV text if too long (keep first 15000 chars ~3750 tokens)
        max_chars = 15000
        if len(cv_text) > max_chars:
            cv_text = cv_text[:max_chars] + "\n...[CV truncated for processing]"

        prompt = f"""Extract this CV into sections. Keep text AS-IS, don't modify.

CV:
{cv_text}

Sections: personal_info, professional_summary, skills, work_experience, education, projects, certifications, additional."""

        try:
            result = self.structured_llm.invoke(prompt)
            return result
        except Exception as e:
            raise Exception(f"Error parsing CV: {str(e)}")

    def parse_cv_for_workspace(self, cv_text: str) -> CVWorkspaceSections:
        """
        Parse CV text into section-specific workspace structure.
        Uses one LLM call for lower latency/cost.
        """
        max_chars = 15000
        if len(cv_text) > max_chars:
            cv_text = cv_text[:max_chars] + "\n...[CV truncated for processing]"

        prompt = f"""Extract this CV into the exact schema.
Keep extracted text close to original CV wording. Do not invent details.

Rules:
1. personal_info: populate name, phone, email, location if found.
2. professional_summary_overview: single summary text field.
3. skills_overview: comma-separated skills string only.
4. work_experience: no overview section; return one entry per employment with fields:
   company_name, location, role, start_date, end_date, currently_working, overview
5. education: no overview section; one entry per institution with fields:
   institution_name, location, degree, start_date, end_date, currently_studying, overview
6. projects: no overview section; one entry per project with project_name and details.
7. certifications: include only if found; one entry per certification with certification_name and details.
8. additional_overview: put any useful content that could not be structured into above fields.

CV:
{cv_text}
"""

        try:
            return self.workspace_structured_llm.invoke(prompt)
        except Exception:
            # Fallback to the simpler parser and split key sections heuristically.
            flat_sections = self.parse_cv(cv_text)
            return self._workspace_from_flat_sections(flat_sections)

    @staticmethod
    def _workspace_from_flat_sections(flat_sections: CVSections) -> CVWorkspaceSections:
        """Convert flat section text into workspace structure with lightweight heuristics."""
        data = flat_sections.model_dump()

        personal = (data.get("personal_info") or "").strip()
        summary = (data.get("professional_summary") or "").strip()
        skills = (data.get("skills") or "").strip()
        work = (data.get("work_experience") or "").strip()
        education = (data.get("education") or "").strip()
        projects = (data.get("projects") or "").strip()
        certifications = (data.get("certifications") or "").strip()

        return CVWorkspaceSections(
            personal_info=CVSectionParser._parse_personal_info(personal),
            professional_summary_overview=summary,
            skills_overview=skills,
            work_experience=CVSectionParser._parse_work_experience(work),
            education=CVSectionParser._parse_education(education),
            projects=CVSectionParser._parse_projects(projects),
            certifications=CVSectionParser._parse_certifications(certifications),
            additional_overview=(data.get("additional") or "").strip(),
        )

    @staticmethod
    def _parse_personal_info(text: str) -> WorkspacePersonalInfo:
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone_match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", text)

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        inferred_name = lines[0] if lines else ""

        location = ""
        if lines:
            for line in lines:
                if "@" in line:
                    continue
                if any(token in line.lower() for token in ["germany", "usa", "uk", "india", "city", ","]):
                    location = line
                    break

        return WorkspacePersonalInfo(
            name=inferred_name,
            phone=phone_match.group(1).strip() if phone_match else "",
            email=email_match.group(0).strip() if email_match else "",
            location=location,
        )

    @staticmethod
    def _split_blocks(text: str) -> list[str]:
        return [block.strip() for block in text.split("\n\n") if block.strip()]

    @staticmethod
    def _parse_work_experience(text: str) -> list[WorkspaceWorkExperienceEntry]:
        entries: list[WorkspaceWorkExperienceEntry] = []
        for block in CVSectionParser._split_blocks(text):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            header = lines[0]
            role = lines[1] if len(lines) > 1 else ""
            details = "\n".join(lines[2:]).strip() if len(lines) > 2 else "\n".join(lines[1:]).strip()

            entries.append(
                WorkspaceWorkExperienceEntry(
                    company_name=header,
                    location="",
                    role=role,
                    start_date="",
                    end_date="",
                    currently_working="present" in block.lower() or "current" in block.lower(),
                    overview=details,
                )
            )

        return entries

    @staticmethod
    def _parse_education(text: str) -> list[WorkspaceEducationEntry]:
        entries: list[WorkspaceEducationEntry] = []
        for block in CVSectionParser._split_blocks(text):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            institution = lines[0]
            degree = lines[1] if len(lines) > 1 else ""
            details = "\n".join(lines[2:]).strip() if len(lines) > 2 else "\n".join(lines[1:]).strip()

            entries.append(
                WorkspaceEducationEntry(
                    institution_name=institution,
                    degree=degree,
                    location="",
                    start_date="",
                    end_date="",
                    currently_studying="present" in block.lower() or "current" in block.lower(),
                    overview=details,
                )
            )

        return entries

    @staticmethod
    def _parse_projects(text: str) -> list[WorkspaceProjectEntry]:
        entries: list[WorkspaceProjectEntry] = []
        for block in CVSectionParser._split_blocks(text):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            entries.append(
                WorkspaceProjectEntry(
                    project_name=lines[0],
                    details="\n".join(lines[1:]).strip() if len(lines) > 1 else block,
                )
            )

        return entries

    @staticmethod
    def _parse_certifications(text: str) -> list[WorkspaceCertificationEntry]:
        entries: list[WorkspaceCertificationEntry] = []
        for block in CVSectionParser._split_blocks(text):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            entries.append(
                WorkspaceCertificationEntry(
                    certification_name=lines[0],
                    details="\n".join(lines[1:]).strip() if len(lines) > 1 else "",
                )
            )

        return entries

    def save_sections(self, sections: CVSections, output_dir: str = "cv_sections") -> Dict[str, str]:
        """
        Save each section to a separate file.

        Args:
            sections: CVSections object
            output_dir: Directory to save sections

        Returns:
            Dictionary mapping section names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)

        saved_files = {}

        section_mapping = {
            "personal_info": "personal_info.txt",
            "professional_summary": "professional_summary.txt",
            "skills": "skills.txt",
            "work_experience": "work_experience.txt",
            "education": "education.txt",
            "projects": "projects.txt",
            "certifications": "certifications.txt",
            "additional": "additional.txt",
        }

        for field_name, filename in section_mapping.items():
            content = getattr(sections, field_name, "")
            if content:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                saved_files[field_name] = filepath

        json_path = os.path.join(output_dir, "sections.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sections.model_dump(), f, indent=2)
        saved_files["json"] = json_path

        return saved_files

    def load_sections(self, section_dir: str = "cv_sections") -> CVSections:
        """
        Load sections from saved files.

        Args:
            section_dir: Directory containing saved sections

        Returns:
            CVSections object
        """
        json_path = os.path.join(section_dir, "sections.json")

        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CVSections(**data)

        raise FileNotFoundError(f"Sections file not found: {json_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python cv_section_parser.py <cv_file>")
        sys.exit(1)

    from .cv_extractor import CVExtractor

    cv_file = sys.argv[1]
    extractor = CVExtractor()
    cv_text = extractor.extract(cv_file)

    print("Parsing CV sections...")
    parser = CVSectionParser()
    sections = parser.parse_cv(cv_text)

    print("Saving sections...")
    saved_files = parser.save_sections(sections)

    print("Sections extracted and saved:")
    for section, filepath in saved_files.items():
        if section != "json":
            print(f"  - {section}: {filepath}")
    print(f"  - Full JSON: {saved_files['json']}")
