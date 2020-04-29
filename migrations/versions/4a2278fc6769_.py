"""empty message

Revision ID: 4a2278fc6769
Revises: d37a2b2da4a6
Create Date: 2020-04-20 16:18:19.872233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a2278fc6769'
down_revision = 'd37a2b2da4a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('timecard', sa.Column('duration', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('timecard', 'duration')
    # ### end Alembic commands ###