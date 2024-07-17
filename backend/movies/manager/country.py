import sys
import asyncio
from pathlib import Path

from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from database.api import ExceptionToHandle
from database.manager import AbstractMovieDataSource, AbstractPersonDataSource
from database.manager import DataBaseManager
from movies.orm import CountryORM
from movies.source import MovieDataSource
from persons.source import PersonDataSource


class CountryManager(DataBaseManager):
    ORM = CountryORM

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

    async def get_countries(self) -> list[CountryORM]:
        async with self.dbapi.session as session:
            return await self.dbapi.mget(CountryORM, session)


async def countries_init():
    manager = CountryManager(MovieDataSource())
    countries = manager.movie_source.get_countries()
    await manager.badd(countries)


if __name__ == "__main__":
    asyncio.run(countries_init())
