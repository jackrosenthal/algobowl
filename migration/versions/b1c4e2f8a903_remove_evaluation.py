"""Remove evaluation

Revision ID: b1c4e2f8a903
Revises: 3e307dd3c114
Create Date: 2026-04-28 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b1c4e2f8a903"
down_revision = "ce07e37e6826"


def upgrade():
    op.drop_table("evaluation")
    op.drop_column("competition", "evaluation_begins")
    op.drop_column("competition", "evaluation_ends")


def downgrade():
    op.add_column(
        "competition",
        sa.Column("evaluation_begins", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "competition",
        sa.Column("evaluation_ends", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "evaluation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("from_student_id", sa.Integer(), nullable=False),
        sa.Column("to_student_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["from_student_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["to_student_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["group.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
