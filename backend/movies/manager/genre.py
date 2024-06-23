import sys
import asyncio
from pathlib import Path
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Any
from sqlalchemy.orm import joinedload
from sqlalchemy import select

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.manager import DatabaseManager
from movies.orm import GenreORM, Base, MovieGenreORM, IMDbMovieORM, TMDbMovieORM
from services.movie_genres import genres


class GenreManager(DatabaseManager):
    ORM = GenreORM

    async def get_genre(
        self,
        slug: str,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Base] | list[tuple[Any]]:
        gq = select(GenreORM)
        gq = gq.where(GenreORM.slug == slug)

        mq = select(IMDbMovieORM)
        mq = mq.join(MovieGenreORM, IMDbMovieORM.id == MovieGenreORM.imdb_movie_id)
        mq = mq.join(GenreORM, MovieGenreORM.genre_id == GenreORM.id)
        mq = mq.options(joinedload(IMDbMovieORM.type))
        mq = mq.options(joinedload(IMDbMovieORM.tmdb))
        mq = mq.where(GenreORM.slug == slug)
        mq = mq.limit(page_size).offset((page - 1) * page_size)

        async with self.dbapi.session as session:
            result = await session.execute(gq)
            genre = result.scalars().first()

            if not genre:
                return None

            result = await session.execute(mq)
            movies = result.scalars().all()

        return genre, movies


async def genres_init(genres):
    manager = GenreManager()
    await manager.goc_batch(genres)


if __name__ == "__main__":
    asyncio.run(genres_init(genres))
