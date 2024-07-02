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

from services.models import IMDbMovieExtraInfo
from database.manager import DatabaseManager, ExceptionToHandle
from movies.orm import IMDbMovieORM
from services.imdb.scraper import (
    IMDbScraper,
    IMDbMovieExtraInfo,
    IMDb404Error,
    IMDb503Error,
    IMDbEmptyResponeError,
)


SCRAPER = IMDbScraper(max_rate=5, rate_period=1)


class IMDbMovieExtraManager(DatabaseManager):
    ORM = IMDbMovieORM

    def __init__(
        self,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(exceptions_to_handle)

    async def add(self, extra_sdm: IMDbMovieExtraInfo) -> None:
        if extra_sdm.error is None:
            async with self.dbapi.session() as session:
                await self.dbapi.update(
                    IMDbMovieORM,
                    session,
                    filters={"imdb_mvid": extra_sdm.imdb_mvid},
                    image_url=extra_sdm.image_url,
                    imdb_extra_added=True,
                )

    async def add_many(
        self,
        extra_sdms: list[IMDbMovieExtraInfo],
    ) -> None:
        tasks = [asyncio.create_task(self.add(extra_sdm)) for extra_sdm in extra_sdms]
        await asyncio.gather(*tasks)


async def imdb_movies_extra_init():
    manager = IMDbMovieExtraManager()
    not_have_extra = await manager.get(
        IMDbMovieORM.imdb_mvid,
        table_model=IMDbMovieORM,
        imdb_extra_added=False,
    )

    tasks = [SCRAPER.get_movie(m.imdb_mvid) for m in not_have_extra]
    movies = await tqdm_asyncio.gather(*tasks)

    await manager.add_many(movies)


if __name__ == "__main__":
    asyncio.run(imdb_movies_extra_init())
