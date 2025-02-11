"""Score type integer

Revision ID: 5f31dcc0e896
Revises: 3e307dd3c114
Create Date: 2022-03-01 10:18:43.827453

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5f31dcc0e896"
down_revision = "3e307dd3c114"


def upgrade():
    with op.batch_alter_table("output") as batch_op:
        batch_op.alter_column(
            "score", type_=sa.BigInteger, postgresql_using="ROUND(score)"
        )


def downgrade():
    with op.batch_alter_table("output") as batch_op:
        batch_op.alter_column("score", type_=sa.Numeric)
