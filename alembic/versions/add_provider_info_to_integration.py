"""add provider_id and provider_name to application_integration_table

Revision ID: add_provider_info_to_integration
Revises: remove_role_priorities
Create Date: 2026-05-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_provider_info_to_integration'
down_revision: Union[str, Sequence[str], None] = 'remove_role_priorities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('application_integration_table', sa.Column('provider_id', sa.UUID(), nullable=False, server_default='00000000-0000-0000-0000-000000000000'))
    op.add_column('application_integration_table', sa.Column('provider_name', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('application_integration_table', 'provider_name')
    op.drop_column('application_integration_table', 'provider_id')
