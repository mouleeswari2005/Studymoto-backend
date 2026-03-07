"""Change duration_minutes to float for decimal precision

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-10 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Change duration_minutes from Integer to Float to support decimal minutes (seconds precision)
    # PostgreSQL uses REAL or DOUBLE PRECISION for float
    op.alter_column('pomodoro_sessions', 'duration_minutes',
                    existing_type=sa.Integer(),
                    type_=sa.Float(),
                    existing_nullable=False,
                    postgresql_using='duration_minutes::double precision')


def downgrade() -> None:
    # Revert back to Integer (will round decimal values)
    op.alter_column('pomodoro_sessions', 'duration_minutes',
                    existing_type=sa.Float(),
                    type_=sa.Integer(),
                    existing_nullable=False,
                    postgresql_using='ROUND(duration_minutes)::integer')




