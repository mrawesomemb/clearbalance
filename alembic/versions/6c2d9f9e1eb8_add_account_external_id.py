"""add account external_id

Revision ID: 6c2d9f9e1eb8
Revises: b219dbac2f23
Create Date: 2026-01-29 18:45:03.367398

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2d9f9e1eb8'
down_revision: Union[str, Sequence[str], None] = 'b219dbac2f23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column nullable first so existing rows don't violate NOT NULL
    op.add_column('accounts', sa.Column('external_id', sa.String(), nullable=True))
    # Backfill existing rows so we can set NOT NULL
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE accounts SET external_id = 'acc-' || id::text WHERE external_id IS NULL"
    ))
    op.alter_column(
        'accounts', 'external_id',
        existing_type=sa.String(),
        nullable=False
    )
    op.create_unique_constraint('uq_accounts_external_id', 'accounts', ['external_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_accounts_external_id', 'accounts', type_='unique')
    op.drop_column('accounts', 'external_id')
