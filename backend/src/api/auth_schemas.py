"""Pydantic schemas for auth/session and user data endpoints."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    message: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class UserDataCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=10000)


class UserDataUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=10000)


class UserDataResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDataListResponse(BaseModel):
    items: list[UserDataResponse]


class CVUploadRequest(BaseModel):
    cv_base64: str = Field(..., min_length=20)
    file_name: str = Field(default="uploaded_cv.pdf", min_length=1, max_length=255)


class CVWorkspacePersonalInfo(BaseModel):
    name: str = Field(default="", max_length=200)
    phone: str = Field(default="", max_length=80)
    email: str = Field(default="", max_length=255)
    location: str = Field(default="", max_length=255)


class CVWorkspaceWorkExperienceEntry(BaseModel):
    company_name: str = Field(default="", max_length=255)
    location: str = Field(default="", max_length=255)
    role: str = Field(default="", max_length=255)
    start_date: str = Field(default="", max_length=80)
    end_date: str = Field(default="", max_length=80)
    currently_working: bool = False
    overview: str = Field(default="", max_length=20000)


class CVWorkspaceEducationEntry(BaseModel):
    institution_name: str = Field(default="", max_length=255)
    location: str = Field(default="", max_length=255)
    degree: str = Field(default="", max_length=255)
    start_date: str = Field(default="", max_length=80)
    end_date: str = Field(default="", max_length=80)
    currently_studying: bool = False
    overview: str = Field(default="", max_length=20000)


class CVWorkspaceProjectEntry(BaseModel):
    project_name: str = Field(default="", max_length=255)
    details: str = Field(default="", max_length=20000)


class CVWorkspaceCertificationEntry(BaseModel):
    certification_name: str = Field(default="", max_length=255)
    details: str = Field(default="", max_length=20000)


class CVWorkspaceSections(BaseModel):
    personal_info: CVWorkspacePersonalInfo = Field(default_factory=CVWorkspacePersonalInfo)
    professional_summary_overview: str = Field(default="", max_length=20000)
    skills_overview: str = Field(default="", max_length=20000)
    work_experience: list[CVWorkspaceWorkExperienceEntry] = Field(default_factory=list)
    education: list[CVWorkspaceEducationEntry] = Field(default_factory=list)
    projects: list[CVWorkspaceProjectEntry] = Field(default_factory=list)
    certifications: list[CVWorkspaceCertificationEntry] = Field(default_factory=list)
    additional_overview: str = Field(default="", max_length=20000)


class CVWorkspaceUpdateRequest(BaseModel):
    sections: CVWorkspaceSections


class CVWorkspaceResponse(BaseModel):
    has_uploaded_cv: bool
    cv_file_name: str | None = None
    sections: CVWorkspaceSections
    updated_at: datetime | None = None
