"""problem type

Revision ID: 6f7d3e38c4d2
Revises: a0614de9cee5
Create Date: 2020-02-18 21:25:44.034035

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6f7d3e38c4d2'
down_revision = 'a0614de9cee5'

problem_type_enum = sa.Enum('minimization', 'maximization', name='ProblemType')


def upgrade():
    problem_type_enum.create(op.get_bind())
    op.add_column('competition',
                  sa.Column('problem_type',
                            problem_type_enum,
                            nullable=True,
                            server_default='minimization'))


def downgrade():
    op.drop_column('competition', 'problem_type')
