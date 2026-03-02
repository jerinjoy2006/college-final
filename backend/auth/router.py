from fastapi import APIRouter, status, Depends
from auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from auth import service
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest):
    user = service.register_user(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        branch=body.branch,
        semester=body.semester,
    )
    token = service.create_access_token(user["id"], user["role"])
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"access_token": token, "token_type": "bearer", "user": safe_user}


@router.post("/login", status_code=status.HTTP_200_OK)
def login(body: LoginRequest):
    user = service.login_user(email=body.email, password=body.password)
    token = service.create_access_token(user["id"], user["role"])
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {"access_token": token, "token_type": "bearer", "user": safe_user}


@router.get("/me", status_code=status.HTTP_200_OK)
def me(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in current_user.items() if k != "password_hash"}
