from fastapi import APIRouter, Depends, status
from registrations.schemas import RegistrationCreate
from registrations import service
from dependencies import get_current_user, require_admin

router = APIRouter(prefix="/registrations", tags=["Registrations"])


@router.get("/me", status_code=status.HTTP_200_OK)
def my_registrations(current_user: dict = Depends(get_current_user)):
    """Get the logged-in student's registrations with event details."""
    return service.get_user_registrations(current_user["id"])


@router.post("", status_code=status.HTTP_201_CREATED)
def register(body: RegistrationCreate, current_user: dict = Depends(get_current_user)):
    """Register the authenticated user for an event (atomic, race-condition safe)."""
    return service.register_for_event(body.event_id, current_user["id"])


@router.delete("/{registration_id}", status_code=status.HTTP_200_OK)
def cancel(registration_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel a registration and atomically restore the seat."""
    return service.cancel_registration(registration_id, current_user["id"])


@router.get("/events/{event_id}", status_code=status.HTTP_200_OK)
def event_registrations(event_id: str, admin_user: dict = Depends(require_admin)):
    """Admin: list all registrations for a specific event."""
    return service.get_event_registrations(event_id, admin_user)
