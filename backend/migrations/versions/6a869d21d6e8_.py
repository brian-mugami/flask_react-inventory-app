"""empty message

Revision ID: 6a869d21d6e8
Revises: 040095bf5147
Create Date: 2023-04-12 16:11:52.642859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a869d21d6e8'
down_revision = '040095bf5147'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=False)

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('buying_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)
        batch_op.alter_column('lines_cost',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=False)

    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.alter_column('amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=True)

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('selling_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)
        batch_op.alter_column('item_cost',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('item_cost',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)
        batch_op.alter_column('selling_price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.alter_column('amount',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=True)

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('lines_cost',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)
        batch_op.alter_column('buying_price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)

    # ### end Alembic commands ###
