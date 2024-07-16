import sys
import asyncio
from pathlib import Path
from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.api import ExceptionToHandle
from movies.orm import ContentTypeORM
from movies.source import MovieDataSource
from persons.source import PersonDataSource
from database.manager import (
    DataBaseManager,
    AbstractMovieDataSource,
    AbstractPersonDataSource,
)


class MovieTypeManager(DataBaseManager):
    ORM = ContentTypeORM

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


async def movie_types_init():
    manager = MovieTypeManager(MovieDataSource())
    movie_types = manager.movie_source.get_content_types()
    await manager.badd(movie_types)


if __name__ == "__main__":
    asyncio.run(movie_types_init())
