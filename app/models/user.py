from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import TIMESTAMP, CheckConstraint, String, UniqueConstraint, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import get_engine
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.job_posting import JobPosting

COLUMNS = "id, name, email, graduation_year, department"


class User(Base):
    """ORM model for the users table (ddd.md section 4.1)."""

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint("graduation_year BETWEEN 1950 AND 2100", name="ck_users_graduation_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    graduation_year: Mapped[int]
    department: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(), server_default=text("CURRENT_TIMESTAMP"))

    # One user -> many job postings. passive_deletes lets PostgreSQL's ON DELETE SET NULL
    # clear posted_by_user_id instead of the ORM loading every posting first.
    job_postings: Mapped[list["JobPosting"]] = relationship(back_populates="posted_by", passive_deletes=True)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class UserCreate(BaseModel):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    graduation_year: int = Field(ge=1950, le=2100)
    department: str = Field(max_length=100)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    department: str | None = Field(default=None, max_length=100)


def _email_taken() -> HTTPException:
    return HTTPException(status_code=409, detail="A user with this email already exists")


def create_user(data: UserCreate) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    f"INSERT INTO users (name, email, graduation_year, department) "
                    f"VALUES (:name, :email, :graduation_year, :department) "
                    f"RETURNING {COLUMNS}"
                ),
                data.model_dump(),
            ).mappings().one()
            return dict(row)
    except IntegrityError as err:
        raise _email_taken() from err


def get_users() -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(f"SELECT {COLUMNS} FROM users ORDER BY id")).mappings().all()
        return [dict(r) for r in rows]


def get_user(user_id: int) -> dict:
    with get_engine().connect() as conn:
        row = conn.execute(
            text(f"SELECT {COLUMNS} FROM users WHERE id = :id"),
            {"id": user_id},
        ).mappings().one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)


def replace_user(user_id: int, data: UserCreate) -> dict:
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    f"UPDATE users "
                    f"SET name = :name, email = :email, graduation_year = :graduation_year, "
                    f"    department = :department, updated_at = CURRENT_TIMESTAMP "
                    f"WHERE id = :id "
                    f"RETURNING {COLUMNS}"
                ),
                {"id": user_id, **data.model_dump()},
            ).mappings().one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail="User not found")
            return dict(row)
    except IntegrityError as err:
        raise _email_taken() from err


def update_user(user_id: int, data: UserUpdate) -> dict:
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        return get_user(user_id)
    set_clause = ", ".join(f"{col} = :{col}" for col in fields)
    try:
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    f"UPDATE users "
                    f"SET {set_clause}, updated_at = CURRENT_TIMESTAMP "
                    f"WHERE id = :id "
                    f"RETURNING {COLUMNS}"
                ),
                {"id": user_id, **fields},
            ).mappings().one_or_none()
            if row is None:
                raise HTTPException(status_code=404, detail="User not found")
            return dict(row)
    except IntegrityError as err:
        raise _email_taken() from err


def delete_user(user_id: int) -> dict:
    with get_engine().begin() as conn:
        result = conn.execute(
            text("DELETE FROM users WHERE id = :id"),
            {"id": user_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted", "id": user_id}
