"""empty message

Revision ID: 89cbc5f01957
Revises: 0e2cb56d5ac3
Create Date: 2023-03-02 12:08:17.502304

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89cbc5f01957'
down_revision = '0e2cb56d5ac3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=2),
               existing_nullable=False)
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_constraint('items_category_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'categories', ['category_id'], ['id'], ondelete='SET DEFAULT')

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)

    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('cost',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=4),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.alter_column('cost',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=4),
               type_=sa.REAL(),
               existing_nullable=False)

    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('items_category_id_fkey', 'categories', ['category_id'], ['id'], ondelete='SET NULL')
        batch_op.alter_column('category_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)

    # ### end Alembic commands ###