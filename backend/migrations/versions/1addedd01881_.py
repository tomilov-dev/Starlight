"""empty message

Revision ID: 1addedd01881
Revises: 0c75764b3c3d
Create Date: 2024-07-17 12:05:30.784113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1addedd01881'
down_revision: Union[str, None] = '0c75764b3c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('token', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['usermodel.id'], name='token_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='token_pkey')
    )
    # ### end Alembic commands ###
