"""update planning models

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2025-01-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update study_plans table to match new schema
    # Drop old columns and add new ones
    op.drop_column('study_plans', 'subject_topic')
    op.drop_column('study_plans', 'study_date')
    op.drop_column('study_plans', 'time')
    op.drop_column('study_plans', 'duration')
    op.drop_column('study_plans', 'notes')
    
    op.add_column('study_plans', sa.Column('title', sa.String(), nullable=False, server_default='Untitled'))
    op.add_column('study_plans', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('study_plans', sa.Column('plan_content', sa.Text(), nullable=True))
    
    # Update summer_vacations table - change date and time to String
    op.alter_column('summer_vacations', 'date',
                    type_=sa.String(),
                    existing_type=sa.Date(),
                    nullable=False)
    op.alter_column('summer_vacations', 'time',
                    type_=sa.String(),
                    existing_type=sa.Time(),
                    nullable=False)
    
    # Update notes table - change date and time to String, make notes nullable
    op.alter_column('notes', 'date',
                    type_=sa.String(),
                    existing_type=sa.Date(),
                    nullable=False)
    op.alter_column('notes', 'time',
                    type_=sa.String(),
                    existing_type=sa.Time(),
                    nullable=False)
    op.alter_column('notes', 'notes',
                    existing_type=sa.Text(),
                    nullable=True)


def downgrade() -> None:
    # Revert study_plans changes
    op.drop_column('study_plans', 'plan_content')
    op.drop_column('study_plans', 'description')
    op.drop_column('study_plans', 'title')
    
    op.add_column('study_plans', sa.Column('subject_topic', sa.String(), nullable=False))
    op.add_column('study_plans', sa.Column('study_date', sa.Date(), nullable=False))
    op.add_column('study_plans', sa.Column('time', sa.Time(), nullable=False))
    op.add_column('study_plans', sa.Column('duration', sa.Integer(), nullable=True))
    op.add_column('study_plans', sa.Column('notes', sa.Text(), nullable=True))
    
    # Revert summer_vacations changes
    op.alter_column('summer_vacations', 'date',
                    type_=sa.Date(),
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('summer_vacations', 'time',
                    type_=sa.Time(),
                    existing_type=sa.String(),
                    nullable=False)
    
    # Revert notes changes
    op.alter_column('notes', 'date',
                    type_=sa.Date(),
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('notes', 'time',
                    type_=sa.Time(),
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('notes', 'notes',
                    existing_type=sa.Text(),
                    nullable=False)




