"""empty message

Revision ID: 5fc66db811bf
Revises: 
Create Date: 2024-04-08 12:34:49.750949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fc66db811bf'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('collection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_en', sa.String(), nullable=False),
    sa.Column('name_ru', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_en'),
    sa.UniqueConstraint('name_ru')
    )
    op.create_table('country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_en', sa.String(), nullable=False),
    sa.Column('name_ru', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_en'),
    sa.UniqueConstraint('name_ru')
    )
    op.create_table('genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('imdb_name', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('tmdb_name', sa.String(), nullable=True),
    sa.Column('name_ru', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('imdb_name'),
    sa.UniqueConstraint('name_ru'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('movie_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_en', sa.String(length=40), nullable=False),
    sa.Column('name_ru', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_en'),
    sa.UniqueConstraint('name_ru')
    )
    op.create_table('imdb_movie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('imdb_mvid', sa.String(length=20), nullable=False),
    sa.Column('movie_type', sa.Integer(), nullable=True),
    sa.Column('title_en', sa.String(), nullable=False),
    sa.Column('title_ru', sa.String(), nullable=True),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('is_adult', sa.Boolean(), nullable=False),
    sa.Column('runtime', sa.SmallInteger(), nullable=True),
    sa.Column('rate', sa.Float(), nullable=True),
    sa.Column('wrate', sa.Float(), nullable=True),
    sa.Column('votes', sa.Integer(), nullable=True),
    sa.Column('imdb_extra_added', sa.Boolean(), nullable=False),
    sa.Column('tmdb_added', sa.Boolean(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['movie_type'], ['movie_type.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('imdb_mvid'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('production_company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country', sa.Integer(), nullable=True),
    sa.Column('name_en', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['country'], ['country.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name_en'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('movie_genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('imdb_movie', sa.Integer(), nullable=False),
    sa.Column('genre', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre'], ['genre.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['imdb_movie'], ['imdb_movie.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tmdb_movie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tmdb_mvid', sa.Integer(), nullable=False),
    sa.Column('imdb_movie', sa.Integer(), nullable=False),
    sa.Column('movie_collection', sa.Integer(), nullable=True),
    sa.Column('release_date', sa.DateTime(), nullable=True),
    sa.Column('budget', sa.BigInteger(), nullable=True),
    sa.Column('revenue', sa.BigInteger(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('tagline_en', sa.Text(), nullable=True),
    sa.Column('overview_en', sa.Text(), nullable=True),
    sa.Column('tagline_ru', sa.Text(), nullable=True),
    sa.Column('overview_ru', sa.Text(), nullable=True),
    sa.Column('rate', sa.Float(), nullable=True),
    sa.Column('votes', sa.Integer(), nullable=True),
    sa.Column('popularity', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['imdb_movie'], ['imdb_movie.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['movie_collection'], ['collection.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('imdb_movie'),
    sa.UniqueConstraint('tmdb_mvid')
    )
    op.create_table('movie_country',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country', sa.Integer(), nullable=False),
    sa.Column('imdb_movie', sa.Integer(), nullable=False),
    sa.Column('tmdb_movie', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['country'], ['country.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['imdb_movie'], ['imdb_movie.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tmdb_movie'], ['tmdb_movie.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movie_production',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('production_company', sa.Integer(), nullable=False),
    sa.Column('imdb_movie', sa.Integer(), nullable=False),
    sa.Column('tmdb_movie', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['imdb_movie'], ['imdb_movie.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['production_company'], ['production_company.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tmdb_movie'], ['tmdb_movie.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('movie_production')
    op.drop_table('movie_country')
    op.drop_table('tmdb_movie')
    op.drop_table('movie_genre')
    op.drop_table('production_company')
    op.drop_table('imdb_movie')
    op.drop_table('movie_type')
    op.drop_table('genre')
    op.drop_table('country')
    op.drop_table('collection')
    # ### end Alembic commands ###