"""apply job posting validation rules

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "job_postings",
        "title",
        existing_type=sa.String(length=200),
        type_=sa.String(length=120),
        existing_nullable=False,
    )
    op.alter_column(
        "job_postings",
        "location",
        existing_type=sa.String(length=150),
        nullable=True,
        existing_nullable=False,
    )
    op.alter_column(
        "job_postings",
        "description",
        existing_type=sa.Text(),
        nullable=True,
        existing_nullable=False,
    )


def downgrade() -> None:
    op.execute("UPDATE job_postings SET location = '' WHERE location IS NULL")
    op.execute("UPDATE job_postings SET description = '' WHERE description IS NULL")
    op.alter_column(
        "job_postings",
        "description",
        existing_type=sa.Text(),
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column(
        "job_postings",
        "location",
        existing_type=sa.String(length=150),
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column(
        "job_postings",
        "title",
        existing_type=sa.String(length=120),
        type_=sa.String(length=200),
        existing_nullable=False,
    )
