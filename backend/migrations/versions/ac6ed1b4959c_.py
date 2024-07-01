"""empty message

Revision ID: ac6ed1b4959c
Revises: f4e0270c11f8
Create Date: 2024-06-22 18:07:02.192624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac6ed1b4959c'
down_revision: Union[str, None] = 'f4e0270c11f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie_genre', sa.Column('imdb_movie_id', sa.Integer(), nullable=False))
    op.add_column('movie_genre', sa.Column('genre_id', sa.Integer(), nullable=False))
    op.drop_constraint('movie_genre_imdb_movie_genre_key', 'movie_genre', type_='unique')
    op.create_unique_constraint(None, 'movie_genre', ['imdb_movie_id', 'genre_id'])
    op.drop_constraint('movie_genre_imdb_movie_fkey', 'movie_genre', type_='foreignkey')
    op.drop_constraint('movie_genre_genre_fkey', 'movie_genre', type_='foreignkey')
    op.create_foreign_key(None, 'movie_genre', 'imdb_movie', ['imdb_movie_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'movie_genre', 'genre', ['genre_id'], ['id'], ondelete='CASCADE')
    op.drop_column('movie_genre', 'imdb_movie')
    op.drop_column('movie_genre', 'genre')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movie_genre', sa.Column('genre', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('movie_genre', sa.Column('imdb_movie', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'movie_genre', type_='foreignkey')
    op.drop_constraint(None, 'movie_genre', type_='foreignkey')
    op.create_foreign_key('movie_genre_genre_fkey', 'movie_genre', 'genre', ['genre'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('movie_genre_imdb_movie_fkey', 'movie_genre', 'imdb_movie', ['imdb_movie'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'movie_genre', type_='unique')
    op.create_unique_constraint('movie_genre_imdb_movie_genre_key', 'movie_genre', ['imdb_movie', 'genre'])
    op.drop_column('movie_genre', 'genre_id')
    op.drop_column('movie_genre', 'imdb_movie_id')
    # ### end Alembic commands ###