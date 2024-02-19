"""add-default-to-input

Revision ID: ce07e37e6826
Revises: 8d2d82cd68f4
Create Date: 2024-02-17 22:30:20.876051

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ce07e37e6826"
down_revision = "8d2d82cd68f4"


def upgrade():
    with op.batch_alter_table("input") as batch_op:
        batch_op.add_column(sa.Column("is_default", sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table("input") as batch_op:
        batch_op.drop_column("is_default")
