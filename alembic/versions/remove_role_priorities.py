"""remove role_priorities from application_table

Revision ID: remove_role_priorities
Revises: 748aa3a6e82d
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_role_priorities'
down_revision: Union[str, Sequence[str], None] = '748aa3a6e82d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('application_table', 'role_priorities')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('application_table', sa.Column('role_priorities', sa.JSON(), nullable=False, server_default='{}'))
