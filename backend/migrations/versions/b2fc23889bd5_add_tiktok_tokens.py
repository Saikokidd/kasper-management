"""add_tiktok_tokens

Revision ID: b2fc23889bd5
Revises: create_tiktok_streams
Create Date: 2026-05-04 13:33:05.360058
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2fc23889bd5'
down_revision: Union[str, None] = 'create_tiktok_streams'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('tiktok_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.String(), nullable=True),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('open_id', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tiktok_tokens_id'), 'tiktok_tokens', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_tiktok_tokens_id'), table_name='tiktok_tokens')
    op.drop_table('tiktok_tokens')
