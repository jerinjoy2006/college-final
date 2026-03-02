from typing import Optional
from fastapi import HTTPException, status
from config import get_supabase


def list_events(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    available_only: bool = False,
    search: Optional[str] = None,
    club_id: Optional[str] = None,
) -> list:
    supabase = get_supabase()
    query = (
        supabase.table("events")
        .select("*, clubs(id, name)")
        .eq("is_active", True)
        .order("event_date", desc=False)
    )
    if date_from:
        query = query.gte("event_date", date_from)
    if date_to:
        query = query.lte("event_date", date_to)
    if category:
        query = query.eq("category", category)
    if available_only:
        query = query.gt("available_seats", 0)
    if club_id:
        query = query.eq("club_id", club_id)
    if search:
        query = query.ilike("title", f"%{search}%")
    result = query.execute()
    return result.data or []


def get_event(event_id: str) -> dict:
    supabase = get_supabase()
    result = (
        supabase.table("events")
        .select("*, clubs(id, name, description)")
        .eq("id", event_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    return result.data


def create_event(data: dict, admin_user: dict) -> dict:
    supabase = get_supabase()
    club_id = data.get("club_id")
    # Verify the admin owns this club
    club = supabase.table("clubs").select("id, admin_id").eq("id", club_id).single().execute()
    if not club.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CLUB_NOT_FOUND", "message": "Club not found"},
        )
    if club.data["admin_id"] != admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You do not manage this club"},
        )
    payload = {
        "club_id": club_id,
        "title": data["title"],
        "description": data.get("description"),
        "category": data.get("category", "Other"),
        "event_date": data["event_date"].isoformat() if hasattr(data["event_date"], "isoformat") else data["event_date"],
        "venue": data.get("venue"),
        "total_seats": data["total_seats"],
        "available_seats": data["total_seats"],
    }
    result = supabase.table("events").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create event")
    return result.data[0]


def update_event(event_id: str, data: dict, admin_user: dict) -> dict:
    supabase = get_supabase()
    event = supabase.table("events").select("*, clubs(admin_id)").eq("id", event_id).single().execute()
    if not event.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    if event.data["clubs"]["admin_id"] != admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You do not manage this event's club"},
        )
    update_payload = {k: v for k, v in data.items() if v is not None}
    if "event_date" in update_payload and hasattr(update_payload["event_date"], "isoformat"):
        update_payload["event_date"] = update_payload["event_date"].isoformat()
    # If total_seats increases, add the delta to available_seats
    if "total_seats" in update_payload:
        old_total = event.data["total_seats"]
        old_available = event.data["available_seats"]
        new_total = update_payload["total_seats"]
        if new_total < old_total - old_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_SEATS",
                    "message": "Cannot reduce total seats below already-registered count",
                },
            )
        update_payload["available_seats"] = old_available + (new_total - old_total)
    result = supabase.table("events").update(update_payload).eq("id", event_id).execute()
    return result.data[0]


def delete_event(event_id: str, admin_user: dict) -> dict:
    supabase = get_supabase()
    event = supabase.table("events").select("*, clubs(admin_id)").eq("id", event_id).single().execute()
    if not event.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    if event.data["clubs"]["admin_id"] != admin_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You do not manage this event's club"},
        )
    supabase.table("events").update({"is_active": False}).eq("id", event_id).execute()
    return {"message": "Event deactivated successfully"}
