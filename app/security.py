import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_engine


class RegisterData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    graduation_year: int = Field(ge=1950, le=2100)
    department: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=72)

    @field_validator("password")
    @classmethod
    def limit_bcrypt_bytes(cls, password: str) -> str:
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return password


class LoginData(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class ProfileData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    graduation_year: int = Field(ge=1950, le=2100)
    department: str = Field(min_length=1, max_length=100)


def _secret_key() -> str:
    secret = os.environ.get("AUTH_SECRET_KEY", "")
    if len(secret) < 32 or secret == "replace_with_a_long_random_secret":
        raise RuntimeError("AUTH_SECRET_KEY must be configured with at least 32 random characters.")
    return secret


def ensure_auth_configured() -> None:
    _secret_key()


def token_ttl_minutes() -> int:
    try:
        ttl = int(os.environ.get("AUTH_TOKEN_TTL_MINUTES", "30"))
    except ValueError as error:
        raise RuntimeError("AUTH_TOKEN_TTL_MINUTES must be a positive integer.") from error
    if ttl <= 0:
        raise RuntimeError("AUTH_TOKEN_TTL_MINUTES must be a positive integer.")
    return ttl


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=token_ttl_minutes()
    )
    return jwt.encode({"sub": str(user_id), "exp": expires}, _secret_key(), algorithm="HS256")


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=["HS256"])
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (jwt.PyJWTError, TypeError, ValueError):
        return None


def get_auth_user(user_id: int) -> dict | None:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, name, email, graduation_year, department, role "
                "FROM users WHERE id = :id"
            ),
            {"id": user_id},
        ).mappings().one_or_none()
    return dict(row) if row else None


def register_user(data: RegisterData) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    "INSERT INTO users (name, email, graduation_year, department, password_hash, role) "
                    "VALUES (:name, :email, :graduation_year, :department, :password_hash, 'user') "
                    "RETURNING id, name, email, graduation_year, department, role"
                ),
                {
                    **data.model_dump(exclude={"password"}),
                    "email": str(data.email).lower(),
                    "password_hash": hash_password(data.password),
                },
            ).mappings().one()
        return dict(row)
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="A user with this email already exists") from error


def authenticate_user(data: LoginData) -> dict | None:
    with get_engine().connect() as conn:
        row = conn.execute(
            text("SELECT id, password_hash FROM users WHERE lower(email) = :email"),
            {"email": str(data.email).lower()},
        ).mappings().one_or_none()
    if row is None or row["password_hash"] is None or not verify_password(data.password, row["password_hash"]):
        return None
    return get_auth_user(row["id"])


def update_profile(user_id: int, data: ProfileData) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    "UPDATE users SET name = :name, email = :email, "
                    "graduation_year = :graduation_year, department = :department, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = :id "
                    "RETURNING id, name, email, graduation_year, department, role"
                ),
                {
                    **data.model_dump(mode="json"),
                    "email": str(data.email).lower(),
                    "id": user_id,
                },
            ).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    except IntegrityError as error:
        raise HTTPException(status_code=409, detail="A user with this email already exists") from error


def list_admin_users() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT id, name, email, graduation_year, department, role FROM users ORDER BY id")
        ).mappings().all()
    return [dict(row) for row in rows]


def admin_counts() -> dict[str, int]:
    with get_engine().connect() as conn:
        return {
            table: conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            for table in ("users", "announcements", "job_postings", "applications")
        }


def update_user_role(user_id: int, role: str) -> None:
    if role not in {"admin", "user"}:
        raise HTTPException(status_code=422, detail="Role must be admin or user")
    with get_engine().begin() as conn:
        current_role = conn.execute(
            text("SELECT role FROM users WHERE id = :id FOR UPDATE"), {"id": user_id}
        ).scalar_one_or_none()
        if current_role is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_role == "admin" and role != "admin":
            admin_count = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'")).scalar_one()
            if admin_count <= 1:
                raise HTTPException(status_code=409, detail="The last administrator cannot be demoted")
        conn.execute(
            text("UPDATE users SET role = :role, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
            {"id": user_id, "role": role},
        )


def delete_admin_user(user_id: int, current_user_id: int) -> None:
    if user_id == current_user_id:
        raise HTTPException(status_code=409, detail="You cannot delete your own account from the admin panel")
    with get_engine().begin() as conn:
        target = conn.execute(
            text("SELECT role FROM users WHERE id = :id FOR UPDATE"), {"id": user_id}
        ).scalar_one_or_none()
        if target is None:
            raise HTTPException(status_code=404, detail="User not found")
        if target == "admin":
            admin_count = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'")).scalar_one()
            if admin_count <= 1:
                raise HTTPException(status_code=409, detail="The last administrator cannot be deleted")
        conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})


def promote_admin(email: str) -> None:
    with get_engine().begin() as conn:
        result = conn.execute(
            text(
                "UPDATE users SET role = 'admin', updated_at = CURRENT_TIMESTAMP "
                "WHERE lower(email) = lower(:email)"
            ),
            {"email": email},
        )
        if result.rowcount == 0:
            raise RuntimeError(f"No user exists with email {email!r}. Register the user first.")


def is_admin(user: dict | None) -> bool:
    return bool(user and user.get("role") == "admin")


def cookie_secure() -> bool:
    return os.environ.get("AUTH_COOKIE_SECURE", "false").lower() == "true"
