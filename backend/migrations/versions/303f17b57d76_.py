"""empty message

Revision ID: 303f17b57d76
Revises: 56a263ab4f10
Create Date: 2024-06-23 14:07:47.495698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '303f17b57d76'
down_revision: Union[str, None] = '56a263ab4f10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('imdb_movie', sa.Column('principals_added', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('imdb_movie', 'principals_added')
    # ### end Alembic commands ###
