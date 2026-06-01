"""add board avatar

Revision ID: 7d2f1c8b4a6e
Revises: f24ce040a43f
Create Date: 2026-05-27 03:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d2f1c8b4a6e"
down_revision: Union[str, Sequence[str], None] = "f24ce040a43f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("boards", sa.Column("avatar_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("boards", "avatar_url")
