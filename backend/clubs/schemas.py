from pydantic import BaseModel, field_validator
from typing import Optional


class ClubCreate(BaseModel):
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Club name cannot be empty")
        return v.strip()


class ClubUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
