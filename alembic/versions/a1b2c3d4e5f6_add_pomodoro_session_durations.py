"""Add pomodoro session durations

Revision ID: a1b2c3d4e5f6
Revises: 6debe5ec38f1
Create Date: 2025-01-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6debe5ec38f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add session duration columns to user_preferences table
    op.add_column('user_preferences', sa.Column('study_duration_minutes', sa.Integer(), nullable=False, server_default='25'))
    op.add_column('user_preferences', sa.Column('short_break_duration_minutes', sa.Integer(), nullable=False, server_default='5'))
    op.add_column('user_preferences', sa.Column('long_break_duration_minutes', sa.Integer(), nullable=False, server_default='15'))


def downgrade() -> None:
    # Remove session duration columns
    op.drop_column('user_preferences', 'long_break_duration_minutes')
    op.drop_column('user_preferences', 'short_break_duration_minutes')
    op.drop_column('user_preferences', 'study_duration_minutes')




