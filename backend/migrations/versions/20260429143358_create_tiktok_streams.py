"""create tiktok_streams

Revision ID: create_tiktok_streams
Revises: rename_mgr_pult
Create Date: 2026-04-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'create_tiktok_streams'
down_revision: Union[str, None] = 'rename_mgr_pult'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
        CREATE TABLE tiktok_streams (
            id SERIAL NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            stream_date TIMESTAMP WITH TIME ZONE NOT NULL,
            views INTEGER NOT NULL DEFAULT 0,
            subscriptions INTEGER NOT NULL DEFAULT 0,
            inquiries INTEGER NOT NULL DEFAULT 0,
            created_by_id INTEGER NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(created_by_id) REFERENCES users (id)
        )
    """)
    op.execute("CREATE INDEX ix_tiktok_streams_id ON tiktok_streams (id)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_tiktok_streams_id")
    op.execute("DROP TABLE IF EXISTS tiktok_streams")
