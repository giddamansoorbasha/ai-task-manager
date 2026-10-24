"""add priority to tasks

Revision ID: ee2158d8c88d
Revises: 51640b27f0ca
Create Date: 2026-10-24 08:57:38.555788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee2158d8c88d'
down_revision: Union[str, Sequence[str], None] = '51640b27f0ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from sqlalchemy.dialects import postgresql

task_priority = postgresql.ENUM("low", "medium", "high", name="taskpriority", create_type=False)

def upgrade() -> None:
    task_priority.create(op.get_bind(), checkfirst=True)
    op.add_column("tasks", sa.Column("priority", task_priority, server_default="medium", nullable=False))

def downgrade() -> None:
    op.drop_column("tasks", "priority")
    task_priority.drop(op.get_bind(), checkfirst=True)