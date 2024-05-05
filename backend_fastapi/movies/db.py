import sys
import asyncio
from pathlib import Path
from typing import Any, Generator, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import DatabaseORM
from movies.orm import (
    IMDbORM,
    GenreORM,
    Base,
    MovieTypeORM,
    CountryORM,
    MovieGenreORM,
    MovieCountryORM,
    MovieProductionORM,
)


MAX_BATCH_SIZE = 500


class MaxBatchSizeExceeded(ValueError):
    def __init__(
        self,
        message: str = "MAX_BATCH_SIZE exceeded",
    ) -> None:
        self.message = message
        super().__init__(self.message)


class MovieDatabaseORM(DatabaseORM):
    """SQLAlchemy async DB API"""

    async def insert_genre(self, genre: GenreORM) -> None:
        await self.insert(genre)

    async def imdb_exists(self, imdb_mvid) -> None:
        query = select(select(IMDbORM).where(IMDbORM.imdb_mvid == imdb_mvid).exists())
        async with self.sf() as session:
            session: AsyncSession
            exists = await session.scalar(query)
            return exists

    async def insert_movie_genre(self, movie_genre: MovieGenreORM) -> None:
        await self.insert(movie_genre)

    async def insert_imdb(self, imdb: IMDbORM) -> None:
        await self.insert(imdb)

    async def insert_movie_production(
        self,
        movie_production: MovieProductionORM,
    ) -> None:
        await self.insert(movie_production)


class MovieDatabaseBatchORM(MovieDatabaseORM):
    """SQLAlchemy async DB API with batch load support"""

    def batching(self, array: list[object]) -> Generator[Any, Any, Any]:
        for i in range(0, len(array), MAX_BATCH_SIZE):
            yield array[i : i + MAX_BATCH_SIZE]

    async def insertb(self, batch: list[Base]) -> None:
        async with self.sf() as session:
            session: AsyncSession
            session.add_all(batch)
            await session.commit()

    async def batch_upload(self, array: list[Base]):
        tasks = [self.insertb(b) for b in self.batching(array)]
        await asyncio.gather(*tasks)

    async def insertb_genres(self, genres: list[GenreORM]) -> None:
        await self.batch_upload(genres)

    async def insertb_movie_types(self, types: list[MovieTypeORM]) -> None:
        await self.batch_upload(types)

    async def insertb_countries(self, countries: list[CountryORM]) -> None:
        await self.batch_upload(countries)

    async def insertb_movie_countries(
        self,
        movie_countries: list[MovieCountryORM],
    ) -> None:
        await self.batch_upload(movie_countries)

    async def insertb_movie_productions(
        self,
        movie_productions: list[MovieProductionORM],
    ) -> None:
        await self.batch_upload(movie_productions)


class MovieDatabaseRaw:
    """Raw async DBAPI"""

    async def insert_imdb(self):
        pass

    async def insertb_imdb(self):
        pass


class MovieDatabase(MovieDatabaseBatchORM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
