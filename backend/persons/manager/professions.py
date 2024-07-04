import sys
import asyncio
from pathlib import Path

from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))


from database.api import ExceptionToHandle
from database.manager import AbstractMovieDataSource, AbstractPersonDataSource
from database.manager import DataBaseManager
from persons.orm import ProfessionORM
from movies.source import MovieDataSource
from persons.source import PersonDataSource


class ProfessionManager(DataBaseManager):
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

    ORM = ProfessionORM


async def professions_init():
    manager = ProfessionManager(
        MovieDataSource(),
        PersonDataSource(),
    )
    professions = manager.person_source.get_professions()

    tasks = [asyncio.create_task(manager.add(p)) for p in professions]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(professions_init())
