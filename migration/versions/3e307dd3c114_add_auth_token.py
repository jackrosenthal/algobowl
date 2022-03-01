"""Add auth token

Revision ID: 3e307dd3c114
Revises: d4e83de702f5
Create Date: 2022-02-28 20:10:32.892745

"""

import alembic.op as op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3e307dd3c114"
down_revision = "d4e83de702f5"


def upgrade():
    op.create_table(
        "auth_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_name", sa.Unicode(), nullable=True),
        sa.Column("client_id", sa.Unicode(), nullable=False),
        sa.Column("date_added", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id"),
    )


def downgrade():
    op.drop_table("auth_token")
