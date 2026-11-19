
"""add health to machines"""

from alembic import op
import sqlalchemy as sa

revision = '94b06228c1d3'
down_revision = '38e81887f4f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'machines',
        sa.Column('health', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('machines', 'health')
