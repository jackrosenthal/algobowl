"""Add Incognito Groups

Revision ID: 819923a3acd9
Revises: 4f7581127c93
Create Date: 2021-10-03 16:04:45.841474

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "819923a3acd9"
down_revision = "4f7581127c93"


def upgrade():
    op.add_column("group", sa.Column("incognito", sa.Boolean, nullable=True))


def downgrade():
    with op.batch_alter_table("group") as batch_op:
        batch_op.drop_column("incognito")
