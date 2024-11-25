"""empty message

Revision ID: 21e525c99a54
Revises: 
Create Date: 2024-11-21 19:13:35.452808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21e525c99a54'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('landlord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=True),
    sa.Column('contact_number', sa.String(length=20), nullable=True),
    sa.Column('address', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('landlord', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_landlord_address'), ['address'], unique=True)
        batch_op.create_index(batch_op.f('ix_landlord_name'), ['name'], unique=False)

    op.create_table('property',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('address', sa.String(length=500), nullable=True),
    sa.Column('start_date', sa.DateTime(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('rent', sa.Float(), nullable=True),
    sa.Column('landlord_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['landlord_id'], ['landlord.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_property_address'), ['address'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('property', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_property_address'))

    op.drop_table('property')
    with op.batch_alter_table('landlord', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_landlord_name'))
        batch_op.drop_index(batch_op.f('ix_landlord_address'))

    op.drop_table('landlord')
    # ### end Alembic commands ###
