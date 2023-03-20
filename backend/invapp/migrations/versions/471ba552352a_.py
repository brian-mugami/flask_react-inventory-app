"""empty message

Revision ID: 471ba552352a
Revises: 0bb60a9e152d
Create Date: 2023-03-20 00:49:49.230778

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '471ba552352a'
down_revision = '0bb60a9e152d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('buying_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('selling_price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('suppliers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('suppliers_account_id_fkey', 'supplier_account', ['account_id'], ['id'], ondelete='SET DEFAULT')

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('selling_price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('buying_price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)

    op.create_table('supplier_account',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('account_name', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.Column('account_description', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('account_number', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_archived', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_unarchived', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('is_archived', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='supplier_account_pkey'),
    sa.UniqueConstraint('account_name', name='supplier_account_account_name_key'),
    sa.UniqueConstraint('account_number', name='supplier_account_account_number_key')
    )
    # ### end Alembic commands ###
