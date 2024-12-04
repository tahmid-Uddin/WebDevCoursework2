"""initial migration

Revision ID: 38b6f96fc308
Revises: 
Create Date: 2024-12-04 20:24:46.869180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38b6f96fc308'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('middle_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('address', sa.String(length=300), nullable=True),
    sa.Column('post_code', sa.String(length=10), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('seller',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('business_name', sa.String(length=100), nullable=False),
    sa.Column('business_phone', sa.String(length=20), nullable=False),
    sa.Column('business_email', sa.String(length=120), nullable=False),
    sa.Column('business_address', sa.String(length=300), nullable=False),
    sa.Column('country', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('listing',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=500), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['seller_id'], ['seller.id'], ),
    sa.PrimaryKeyConstraint('product_id')
    )
    op.create_table('orders',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('seller_id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=500), nullable=False),
    sa.Column('product_description', sa.Text(), nullable=False),
    sa.Column('product_price', sa.Float(), nullable=False),
    sa.Column('product_created_at', sa.DateTime(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('order_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['seller_id'], ['seller.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('order_id')
    )
    op.create_table('cart',
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['listing.product_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('cart_id')
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['listing.product_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('wishlist_table',
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['listing.product_id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wishlist_table')
    op.drop_table('image')
    op.drop_table('cart')
    op.drop_table('orders')
    op.drop_table('listing')
    op.drop_table('seller')
    op.drop_table('user')
    # ### end Alembic commands ###