from fastapi import APIRouter, Depends, status
from clubs.schemas import ClubCreate, ClubUpdate
from clubs import service
from dependencies import require_admin

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("", status_code=status.HTTP_200_OK)
def list_clubs():
    return service.list_clubs()


@router.get("/{club_id}", status_code=status.HTTP_200_OK)
def get_club(club_id: str):
    return service.get_club(club_id)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_club(body: ClubCreate, admin_user: dict = Depends(require_admin)):
    return service.create_club(body.name, body.description, admin_user)


@router.patch("/{club_id}", status_code=status.HTTP_200_OK)
def update_club(club_id: str, body: ClubUpdate, admin_user: dict = Depends(require_admin)):
    return service.update_club(club_id, body.model_dump(), admin_user)
