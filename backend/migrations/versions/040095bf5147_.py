"""empty message

Revision ID: 040095bf5147
Revises: 629a1926b5f1
Create Date: 2023-04-10 16:00:04.607441

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '040095bf5147'
down_revision = '629a1926b5f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('inventory balances', schema=None) as batch_op:
        batch_op.drop_constraint('inventory balances_item_id_invoice_id_key', type_='unique')
        batch_op.create_unique_constraint(None, ['item_id', 'invoice_id', 'receipt_id'])

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
        batch_op.drop_column('lines_cost')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lines_cost', sa.REAL(), autoincrement=False, nullable=False))
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

    with op.batch_alter_table('inventory balances', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('inventory balances_item_id_invoice_id_key', ['item_id', 'invoice_id'])

    # ### end Alembic commands ###
