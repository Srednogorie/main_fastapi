"""add foo tables

Revision ID: 4
Revises: 3
Create Date: 2022-11-24 23:02:59.604810

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4'
down_revision = '3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_product_id'), 'product', ['id'], unique=False)

    op.create_table('order',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('total', sa.Integer(), nullable=True),
                    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_order_id'), 'order', ['id'], unique=False)

    op.create_table('order_item',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=True),
                    sa.Column('product_id', sa.Integer(), nullable=True),
                    sa.Column('quantity', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
                    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('order_id', 'product_id', name='_order_product_uc')
                    )
    op.create_index(op.f('ix_order_item_id'), 'order_item', ['id'], unique=False)

    op.create_table('product_order_association',
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
                    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
                    sa.PrimaryKeyConstraint('product_id', 'order_id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_order_association')
    op.drop_index(op.f('ix_order_item_id'), table_name='order_item')
    op.drop_table('order_item')
    op.drop_index(op.f('ix_order_id'), table_name='order')
    op.drop_table('order')
    op.drop_index(op.f('ix_product_id'), table_name='product')
    op.drop_table('product')
    # ### end Alembic commands ###
