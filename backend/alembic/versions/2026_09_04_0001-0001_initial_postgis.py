"""enable postgis extension

Revision ID: 0001_initial_postgis
Revises:
Create Date: 2026-09-04 15:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_postgis"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure PostGIS extension is enabled in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")


def downgrade() -> None:
    # Drop PostGIS extension with CASCADE to cleanly clean up dependent sub-extensions if necessary
    op.execute("DROP EXTENSION IF EXISTS postgis CASCADE;")
