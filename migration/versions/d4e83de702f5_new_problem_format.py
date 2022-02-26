"""New Problem Format

Revision ID: d4e83de702f5
Revises: 819923a3acd9
Create Date: 2022-02-25 13:42:57.559285

"""

import sqlalchemy as sa
from alembic import op
from depot.fields.sqlalchemy import UploadedFileField

# revision identifiers, used by Alembic.
revision = "d4e83de702f5"
down_revision = "819923a3acd9"

problem_type_enum = sa.Enum("minimization", "maximization", name="ProblemType")


def upgrade():
    with op.batch_alter_table("competition") as batch_op:
        batch_op.drop_column("problem_id")
        batch_op.add_column(sa.Column("problem", sa.String, nullable=True))

    op.drop_table("problem")


def downgrade():
    op.create_table(
        "problem",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("input_verifier", UploadedFileField, nullable=False),
        sa.Column("output_verifier", UploadedFileField, nullable=False),
        sa.Column(
            "problem_type", problem_type_enum, nullable=False, default="minimization"
        ),
        sa.Column("problem_statement", UploadedFileField, nullable=True),
    )
