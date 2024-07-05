import sys
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from database.manager import AbstractPersonDataSource, AbstractMovieDataSource
from movies.source import MovieDataSource, IMDbMovieExtraInfoSourceDM
from persons.source import PersonDataSource
from database.manager import DataBaseManager, ExceptionToHandle
from movies.orm import IMDbMovieORM


class IMDbMovieExtraManager(DataBaseManager):
    ORM = IMDbMovieORM

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

    async def add(self, extra_sdm: IMDbMovieExtraInfoSourceDM) -> None:
        if extra_sdm.error is None:
            async with self.dbapi.session as session:
                await self.dbapi.update(
                    IMDbMovieORM,
                    session,
                    filters={"imdb_mvid": extra_sdm.imdb_mvid},
                    image_url=extra_sdm.image_url,
                    imdb_extra_added=True,
                )


async def imdb_movies_extra_init():
    manager = IMDbMovieExtraManager()

    async with manager.dbapi.session as session:
        not_have_extra = await manager.dbapi.mget(
            IMDbMovieORM,
            session,
            IMDbMovieORM.imdb_mvid,
            imdb_extra_added=False,
        )

    tasks = [
        manager.movie_source.get_imdb_movie_extra(m.imdb_mvid) for m in not_have_extra
    ]
    movies_extra = await tqdm_asyncio.gather(*tasks)

    tasks = [manager.add(me) for me in movies_extra]
    await tqdm_asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(imdb_movies_extra_init())
