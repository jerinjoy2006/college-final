from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from events.schemas import EventCreate, EventUpdate
from events import service
from dependencies import get_current_user_optional, require_admin

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", status_code=status.HTTP_200_OK)
def list_events(
    date_from: Optional[str] = Query(None, description="ISO date string"),
    date_to: Optional[str] = Query(None, description="ISO date string"),
    category: Optional[str] = Query(None),
    available_only: bool = Query(False),
    search: Optional[str] = Query(None),
    club_id: Optional[str] = Query(None),
):
    return service.list_events(
        date_from=date_from,
        date_to=date_to,
        category=category,
        available_only=available_only,
        search=search,
        club_id=club_id,
    )


@router.get("/{event_id}", status_code=status.HTTP_200_OK)
def get_event(event_id: str):
    return service.get_event(event_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(body: EventCreate, admin_user: dict = Depends(require_admin)):
    return service.create_event(body.model_dump(), admin_user)


@router.patch("/{event_id}", status_code=status.HTTP_200_OK)
def update_event(event_id: str, body: EventUpdate, admin_user: dict = Depends(require_admin)):
    return service.update_event(event_id, body.model_dump(), admin_user)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
def delete_event(event_id: str, admin_user: dict = Depends(require_admin)):
    return service.delete_event(event_id, admin_user)
