import sys
import asyncio
from enum import Enum
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

from movies.manager.imdb_movie import MoviesOrderBy
from movies.models import IMDbMovieBaseDTO
from database.api import ExceptionToHandle
from movies.orm import IMDbMovieORM, MovieGenreORM, GenreORM, BaseORM
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

    async def get_genres(self):
        async with self.dbapi.session as session:
            return await self.dbapi.mget(GenreORM, session)


async def genres_init():
    manager = GenreManager(MovieDataSource())
    genres = manager.movie_source.get_genres()
    await manager.badd(genres)


if __name__ == "__main__":
    asyncio.run(genres_init())
