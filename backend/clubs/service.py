from fastapi import HTTPException, status
from config import get_supabase


def list_clubs() -> list:
    supabase = get_supabase()
    result = supabase.table("clubs").select("*").execute()
    return result.data or []


def get_club(club_id: str) -> dict:
    supabase = get_supabase()
    result = supabase.table("clubs").select("*").eq("id", club_id).single().execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "CLUB_NOT_FOUND", "message": "Club not found"},
        )
    return result.data


def create_club(name: str, description: str | None, admin_user: dict) -> dict:
    supabase = get_supabase()
    existing = supabase.table("clubs").select("id").eq("name", name).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CLUB_EXISTS", "message": "A club with this name already exists"},
        )
    result = supabase.table("clubs").insert(
        {"name": name, "description": description, "admin_id": admin_user["id"]}
    ).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create club")
    return result.data[0]


def update_club(club_id: str, data: dict, admin_user: dict) -> dict:
    supabase = get_supabase()
    club = supabase.table("clubs").select("*").eq("id", club_id).single().execute()
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
    update_payload = {k: v for k, v in data.items() if v is not None}
    result = supabase.table("clubs").update(update_payload).eq("id", club_id).execute()
    return result.data[0]
