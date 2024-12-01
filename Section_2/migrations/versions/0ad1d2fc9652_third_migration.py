"""third migration

Revision ID: 0ad1d2fc9652
Revises: b8c6be599acd
Create Date: 2024-12-01 14:57:35.232781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ad1d2fc9652'
down_revision = 'b8c6be599acd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.TEXT(), nullable=True))
        batch_op.alter_column('url',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)

    # ### end Alembic commands ###