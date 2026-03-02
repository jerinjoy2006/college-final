from datetime import datetime, timedelta
import bcrypt
from jose import jwt
from config import settings, get_supabase
from fastapi import HTTPException, status


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def register_user(email: str, password: str, full_name: str, branch: str, semester: int) -> dict:
    """Register a new student user. Admins are pre-seeded and cannot self-register."""
    supabase = get_supabase()
    existing = supabase.table("users").select("id").eq("email", email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "EMAIL_EXISTS", "message": "An account with this email already exists"},
        )
    hashed = hash_password(password)
    result = supabase.table("users").insert(
        {
            "email": email,
            "password_hash": hashed,
            "full_name": full_name,
            "role": "student",
            "branch": branch,
            "semester": semester,
        }
    ).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return result.data[0]


def login_user(email: str, password: str) -> dict:
    supabase = get_supabase()
    result = supabase.table("users").select("*").eq("email", email).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )
    user = result.data[0]
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"},
        )
    return user
