"""rename manager to pult and create ads job_posts

Revision ID: rename_mgr_pult
Revises: ad933b7f0ee9
Create Date: 2026-04-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'rename_mgr_pult'
down_revision: Union[str, None] = 'ad933b7f0ee9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("ALTER TYPE userrole RENAME VALUE 'manager' TO 'pult'")

    op.execute("CREATE TYPE adplatform AS ENUM ('telegram', 'facebook', 'instagram', 'tiktok')")
    op.execute("CREATE TYPE jobplatform AS ENUM ('olx', 'workua')")
    op.execute("CREATE TYPE jobpoststatus AS ENUM ('active', 'blocked')")

    op.execute("""
        CREATE TABLE ads (
            id SERIAL NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            platform adplatform NOT NULL,
            published_at TIMESTAMP WITH TIME ZONE,
            created_by_id INTEGER NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(created_by_id) REFERENCES users (id)
        )
    """)
    op.execute("CREATE INDEX ix_ads_id ON ads (id)")

    op.execute("""
        CREATE TABLE job_posts (
            id SERIAL NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            platform jobplatform NOT NULL,
            content TEXT,
            published_at TIMESTAMP WITH TIME ZONE,
            responses INTEGER DEFAULT 0,
            comment TEXT,
            status jobpoststatus NOT NULL DEFAULT 'active',
            block_reason TEXT,
            created_by_id INTEGER NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(created_by_id) REFERENCES users (id)
        )
    """)
    op.execute("CREATE INDEX ix_job_posts_id ON job_posts (id)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_job_posts_id")
    op.execute("DROP TABLE IF EXISTS job_posts")
    op.execute("DROP INDEX IF EXISTS ix_ads_id")
    op.execute("DROP TABLE IF EXISTS ads")
    op.execute("DROP TYPE IF EXISTS jobpoststatus")
    op.execute("DROP TYPE IF EXISTS jobplatform")
    op.execute("DROP TYPE IF EXISTS adplatform")
    op.execute("ALTER TYPE userrole RENAME VALUE 'pult' TO 'manager'")
