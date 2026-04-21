"""Remove category_id from incomes

Revision ID: remove_category_id_incomes
Revises: 25e22fff706b
Create Date: 2025-04-20 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "remove_category_id_incomes"
down_revision: Union[str, None] = "25e22fff706b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("incomes", "category_id")


def downgrade() -> None:
    op.add_column("incomes", sa.Column("category_id", sa.Integer(), nullable=True))
