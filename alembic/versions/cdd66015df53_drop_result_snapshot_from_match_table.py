"""drop result_snapshot from match_table

Revision ID: cdd66015df53
Revises: 4f3d2e410643
Create Date: 2026-05-17 13:40:11.297001

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdd66015df53'
down_revision: Union[str, Sequence[str], None] = '4f3d2e410643'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('match_table', 'result_snapshot')


def downgrade() -> None:
    op.add_column('match_table', sa.Column('result_snapshot', sa.JSON(), nullable=True))
