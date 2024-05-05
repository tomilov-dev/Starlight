import sys
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import IMDbORM
from services.imdb.scraper import (
    IMDbScraper,
    IMDbMovieExtraInfo,
    IMDb404Error,
    IMDb503Error,
    IMDbEmptyResponeError,
)


SCRAPER = IMDbScraper(max_rate=2, rate_period=1)


class IMDbExtraAdder(DatabaseAdder):
    def __init__(self) -> None:
        super().__init__()

        self.scraper = SCRAPER

    async def mark_up(self, imdb_mvid: str, session: AsyncSession) -> None:
        await self.mvdb.update(
            IMDbORM,
            session,
            filters={"imdb_mvid": imdb_mvid},
            imdb_extra_added=True,
        )

    async def add(self, imdb_mvid: str) -> None:
        extra_info = None
        try:
            extra_info: IMDbMovieExtraInfo = await self.scraper.get_movie(
                imdb_mvid,
            )
        except IMDb503Error as ex:
            extra_info = None
            print(ex)

        if extra_info:
            async with self.mvdb.session as session:
                image_url = extra_info.image_url
                await self.mvdb.update(
                    IMDbORM,
                    session,
                    filters={"imdb_mvid": imdb_mvid},
                    image_url=image_url,
                )
                await self.mark_up(imdb_mvid, session)
                await session.commit()

    async def add_all(self) -> None:
        async with self.mvdb.session as session:
            imdbs: list[IMDbORM] = await self.mvdb.get(
                IMDbORM,
                session,
                IMDbORM.id,
                IMDbORM.imdb_mvid,
                imdb_extra_added=False,
            )

        if len(imdbs) > 0:
            tasks = [self.add(m.imdb_mvid) for m in imdbs]

            print("Insert IMDb Movie Extra Info")
            await tqdm_asyncio.gather(*tasks)


async def main():
    adder = IMDbExtraAdder()
    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
