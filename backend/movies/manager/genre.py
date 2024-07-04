import sys
import asyncio
from pathlib import Path
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import Any
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.api import ExceptionToHandle
from movies.orm import GenreORM
from movies.source import MovieDataSource
from persons.source import PersonDataSource
from database.manager import (
    DataBaseManager,
    AbstractPersonDataSource,
    AbstractMovieDataSource,
)


class GenreManager(DataBaseManager):
    def __init__(
        self,
        movie_source: AbstractMovieDataSource = MovieDataSource(),
        person_source: AbstractPersonDataSource = PersonDataSource(),
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(
            movie_source=movie_source,
            person_source=person_source,
            exceptions_to_handle=exceptions_to_handle,
        )

    ORM = GenreORM

    # async def get_genre(
    #     self,
    #     slug: str,
    #     page: int = 1,
    #     page_size: int = 10,
    #     sess: AsyncSession | None = None,
    # ) -> list[BaseORM] | list[tuple[Any]]:
    #     gq = select(GenreORM)
    #     gq = gq.where(GenreORM.slug == slug)

    #     mq = select(IMDbMovieORM)
    #     mq = mq.join(MovieGenreORM, IMDbMovieORM.id == MovieGenreORM.imdb_movie_id)
    #     mq = mq.join(GenreORM, MovieGenreORM.genre_id == GenreORM.id)
    #     mq = mq.options(joinedload(IMDbMovieORM.type))
    #     mq = mq.options(joinedload(IMDbMovieORM.tmdb))
    #     mq = mq.where(GenreORM.slug == slug)
    #     mq = mq.limit(page_size).offset((page - 1) * page_size)

    #     async with self.dbapi.session(sess) as session:
    #         result = await session.execute(gq)
    #         genre = result.scalars().first()

    #         if not genre:
    #             return None

    #         result = await session.execute(mq)
    #         movies = result.scalars().all()

    #     return genre, movies


async def genres_init():
    manager = GenreManager(MovieDataSource())
    genres = manager.movie_source.get_genres()
    await manager.badd(genres)


if __name__ == "__main__":
    asyncio.run(genres_init())
