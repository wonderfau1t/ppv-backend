"""Added new type for user statuses

Revision ID: 3560e1265b6b
Revises: d145ac8420b6
Create Date: 2025-12-14 21:47:48.536032

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3560e1265b6b"
down_revision: Union[str, Sequence[str], None] = "d145ac8420b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_status_enum = sa.Enum("PENDING", "ACTIVE", "BLOCKED", name="user_status")


def upgrade() -> None:
    """Upgrade schema."""
    user_status_enum.create(op.get_bind())

    op.add_column(
        "users_auth",
        sa.Column("status", user_status_enum, nullable=False, default="PENDING"),
    )

    op.alter_column(
        "users_auth",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users_auth", "status")
    user_status_enum.drop(op.get_bind())
