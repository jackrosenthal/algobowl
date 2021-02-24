"""Separate Competitions and Problems

Revision ID: 4f7581127c93
Revises: 6f7d3e38c4d2
Create Date: 2021-02-23 12:55:36.771977

"""

import sqlalchemy as sa

from alembic import op
from depot.fields.sqlalchemy import UploadedFileField

problem_type_enum = sa.Enum('minimization', 'maximization', name='ProblemType')

# revision identifiers, used by Alembic.
revision = '4f7581127c93'
down_revision = '6f7d3e38c4d2'


def upgrade():
    op.create_table(
        'problem',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('input_verifier', UploadedFileField, nullable=False),
        sa.Column('output_verifier', UploadedFileField, nullable=False),
        sa.Column('problem_type', problem_type_enum, nullable=False,
                  default='minimization'),
        sa.Column('problem_statement', UploadedFileField, nullable=True),
    )

    op.execute('''
         INSERT INTO problem
             (id, name, input_verifier, output_verifier, problem_type,
              problem_statement)
         SELECT id, name, input_verifier, output_verifier, problem_type,
                problem_statement FROM competition''')

    op.add_column(
        'competition',
        sa.Column('problem_id', sa.Integer(), nullable=False,
                  server_default='-1'))

    op.execute('UPDATE competition SET problem_id = id')

    with op.batch_alter_table('competition') as batch_op:
        batch_op.drop_column('input_verifier')
        batch_op.drop_column('output_verifier')
        batch_op.drop_column('problem_type')
        batch_op.drop_column('problem_statement')
        batch_op.alter_column('problem_id', sa.ForeignKey('problem.id'),
                              server_default=None)


def downgrade():
    with op.batch_alter_table('competition') as batch_op:
        batch_op.add_column(
            sa.Column('input_verifier', UploadedFileField, nullable=True))
        batch_op.add_column(
            sa.Column('output_verifier', UploadedFileField, nullable=True))
        batch_op.add_column(
            sa.Column('problem_statement', UploadedFileField, nullable=True))
        batch_op.add_column(
            sa.Column('problem_type', problem_type_enum, nullable=False,
                      server_default='minimization'))

    op.execute('UPDATE competition SET {}'.format(
        ', '.join(
            '{0} = '
            '(SELECT {0} FROM problem WHERE problem.id = problem_id)'.format(
                column_name)
            for column_name in ('input_verifier', 'output_verifier',
                                'problem_statement', 'problem_type'))))

    with op.batch_alter_table('competition') as batch_op:
        batch_op.drop_column('problem_id')
        batch_op.alter_column('input_verifier', nullable=False)
        batch_op.alter_column('output_verifier', nullable=False)

    op.drop_table('problem')
