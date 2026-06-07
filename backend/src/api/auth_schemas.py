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


class CVWorkspaceUpdateRequest(BaseModel):
    sections: dict[str, str]


class CVWorkspaceResponse(BaseModel):
    has_uploaded_cv: bool
    cv_file_name: str | None = None
    sections: dict[str, str]
    updated_at: datetime | None = None
