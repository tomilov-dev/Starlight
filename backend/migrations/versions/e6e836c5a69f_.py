"""empty message

Revision ID: e6e836c5a69f
Revises: 5fc66db811bf
Create Date: 2024-05-03 14:08:27.190216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6e836c5a69f'
down_revision: Union[str, None] = '5fc66db811bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('genre', sa.Column('image_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('genre', 'image_url')
    # ### end Alembic commands ###
