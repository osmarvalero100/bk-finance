"""Create fixed expenses table

Revision ID: create_fixed_expenses
Revises: remove_category_id_incomes
Create Date: 2026-09-12 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'create_fixed_expenses'
down_revision: Union[str, None] = 'remove_category_id_incomes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'fixed_expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('payment_method_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='COP'),
        sa.Column('due_day', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(length=50), nullable=False, server_default='monthly'),
        sa.Column('reminder_days_before', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('email_reminder_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_reminder_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fixed_expenses_id'), 'fixed_expenses', ['id'], unique=False)
    op.create_index(op.f('ix_fixed_expenses_user_id'), 'fixed_expenses', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_fixed_expenses_user_id'), table_name='fixed_expenses')
    op.drop_index(op.f('ix_fixed_expenses_id'), table_name='fixed_expenses')
    op.drop_table('fixed_expenses')
