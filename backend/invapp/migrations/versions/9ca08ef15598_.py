"""empty message

Revision ID: 9ca08ef15598
Revises: 21b7c17a686b
Create Date: 2023-03-02 14:53:12.110659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ca08ef15598'
down_revision = '21b7c17a686b'
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
        batch_op.alter_column('price',
               existing_type=sa.Float(precision=2),
               type_=sa.REAL(),
               existing_nullable=False)

    # ### end Alembic commands ###
