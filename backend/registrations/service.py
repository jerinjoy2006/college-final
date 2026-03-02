from fastapi import HTTPException, status
from config import get_supabase


def register_for_event(event_id: str, user_id: str) -> dict:
    """
    Calls the atomic PostgreSQL function book_event_seat to safely
    register a user for an event, preventing race conditions and overbooking.
    """
    supabase = get_supabase()
    try:
        result = supabase.rpc("book_event_seat", {
            "p_event_id": event_id,
            "p_user_id": user_id
        }).execute()
        return result.data
    except Exception as e:
        err = str(e)
        if "EVENT_NOT_FOUND" in err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "EVENT_NOT_FOUND", "message": "Event not found"},
            )
        if "EVENT_INACTIVE" in err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "EVENT_INACTIVE", "message": "Event is no longer active"},
            )
        if "DUPLICATE_REGISTRATION" in err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "DUPLICATE_REGISTRATION", "message": "You are already registered for this event"},
            )
        if "NO_SEATS_AVAILABLE" in err:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "NO_SEATS_AVAILABLE", "message": "This event is fully booked"},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "REGISTRATION_ERROR", "message": "Registration failed"},
        )


def cancel_registration(registration_id: str, user_id: str) -> dict:
    """
    Calls the atomic PostgreSQL function cancel_event_registration 
    to safely cancel and restore seat count.
    """
    supabase = get_supabase()
    try:
        result = supabase.rpc("cancel_event_registration", {
            "p_registration_id": registration_id,
            "p_user_id": user_id
        }).execute()
        return result.data
    except Exception as e:
        err = str(e)
        if "REGISTRATION_NOT_FOUND" in err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "REGISTRATION_NOT_FOUND", "message": "Registration not found"},
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "CANCELLATION_ERROR", "message": "Cancellation failed"},
        )


def get_user_registrations(user_id: str) -> list:
    supabase = get_supabase()
    result = (
        supabase.table("registrations")
        .select("*, events(id, title, description, category, event_date, venue, available_seats, total_seats, is_active, clubs(name))")
        .eq("user_id", user_id)
        .order("registered_at", desc=True)
        .execute()
    )
    return result.data or []


def get_event_registrations(event_id: str, admin_user: dict) -> list:
    supabase = get_supabase()
    # Verify admin owns the club that hosts this event
    event = supabase.table("events").select("*, clubs(admin_id)").eq("id", event_id).single().execute()
    if not event.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    if event.data["clubs"]["admin_id"] != admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You do not manage this event"},
        )
    result = (
        supabase.table("registrations")
        .select("*, users(id, full_name, email)")
        .eq("event_id", event_id)
        .order("registered_at", desc=True)
        .execute()
    )
    return result.data or []
