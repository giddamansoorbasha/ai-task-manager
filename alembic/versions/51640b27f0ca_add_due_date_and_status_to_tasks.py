"""add due_date and status to tasks

Revision ID: 51640b27f0ca
Revises: 58aa41910d7d
Create Date: 2026-10-04 14:50:27.310579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51640b27f0ca'
down_revision: Union[str, Sequence[str], None] = '58aa41910d7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy.dialects import postgresql

task_status = postgresql.ENUM("todo", "in_progress", "done", name="taskstatus", create_type=False)

def upgrade() -> None:
    task_status.create(op.get_bind(), checkfirst=True)
    op.add_column("tasks", sa.Column("due_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tasks", sa.Column("status", task_status, server_default="todo", nullable=False))

def downgrade() -> None:
    op.drop_column("tasks", "status")
    op.drop_column("tasks", "due_date")
    task_status.drop(op.get_bind(), checkfirst=True)