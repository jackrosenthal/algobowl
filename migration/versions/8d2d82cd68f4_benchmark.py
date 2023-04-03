"""Benchmark

Revision ID: 8d2d82cd68f4
Revises: 5f31dcc0e896
Create Date: 2023-03-27 08:50:36.391618

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d2d82cd68f4"
down_revision = "5f31dcc0e896"


def upgrade():
    op.add_column("group", sa.Column("benchmark", sa.Boolean, nullable=True))


def downgrade():
    with op.batch_alter_table("group") as batch_op:
        batch_op.drop_column("benchmark")
