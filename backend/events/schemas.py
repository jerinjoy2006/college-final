from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime

VALID_CATEGORIES = [
    "Coding", "Robotics", "Design", "Music", "Sports",
    "Cultural", "Science", "Business", "Workshop", "Other"
]


class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "Other"
    event_date: datetime
    venue: Optional[str] = None
    total_seats: int
    club_id: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("total_seats")
    @classmethod
    def seats_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("total_seats must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[datetime] = None
    venue: Optional[str] = None
    total_seats: Optional[int] = None
    is_active: Optional[bool] = None

    @field_validator("total_seats")
    @classmethod
    def seats_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("total_seats must be greater than 0")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {VALID_CATEGORIES}")
        return v
