"""empty message

Revision ID: 0c2a4643cde8
Revises: 4c0fb5abb21d
Create Date: 2023-04-06 01:07:39.433935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c2a4643cde8'
down_revision = '4c0fb5abb21d'
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
        batch_op.add_column(sa.Column('status', sa.Enum('fully paid', 'partially paid', 'not paid', 'over paid', name='invoice_status'), nullable=True))
        batch_op.add_column(sa.Column('matched_to_lines', sa.Enum('matched', 'unmatched', 'partially matched', name='invoice_matched_types'), nullable=False))
        batch_op.alter_column('amount',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=True)
        batch_op.drop_column('accounted')

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('selling_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('selling_price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('receipts', schema=None) as batch_op:
        batch_op.alter_column('accounted',
               existing_type=sa.Enum('fully_accounted', 'partially_accounted', 'not_accounted', name='accounting_status'),
               type_=sa.BOOLEAN(),
               existing_nullable=True)
        batch_op.alter_column('amount',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=True)
        batch_op.drop_column('matched_to_lines')
        batch_op.drop_column('status')

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