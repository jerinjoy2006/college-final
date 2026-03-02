from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
import re


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    full_name: str
    branch: str
    semester: int


    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        pwd = info.data.get("password")
        if pwd and v != pwd:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()

    @field_validator("branch")
    @classmethod
    def branch_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Branch cannot be empty")
        return v.strip()

    @field_validator("semester")
    @classmethod
    def semester_valid(cls, v: int) -> int:
        if v < 1 or v > 10:
            raise ValueError("Semester must be between 1 and 10")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    branch: Optional[str] = None
    semester: Optional[int] = None
    created_at: str
