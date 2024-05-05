import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import IMDbORM
from services.imdb.scraper import IMDbScraper, IMDbMovieExtraInfo


SCRAPER = IMDbScraper(max_rate=10, rate_period=1)


class IMDbExtraAdder(DatabaseAdder):
    def __init__(self) -> None:
        super().__init__()

        self.scraper = SCRAPER

    async def mark_up(self, imdb_mvid: str) -> None:
        await self.mvdb.update(
            IMDbORM,
            filters={"imdb_mvid": imdb_mvid},
            imdb_extra_added=True,
        )

    async def add(self, imdb_mvid: str) -> None:
        extra_info: IMDbMovieExtraInfo = await self.scraper.get_movie(
            imdb_mvid,
        )

        image_url = extra_info.image_url
        await self.mvdb.update(
            IMDbORM,
            filters={"imdb_mvid": imdb_mvid},
            image_url=image_url,
        )
        await self.mark_up(imdb_mvid)

    async def add_all(self) -> None:
        imdb: list[IMDbORM] = await self.mvdb.get(
            IMDbORM,
            IMDbORM.id,
            IMDbORM.imdb_mvid,
            imdb_extra_added=False,
        )

        if len(imdb) > 0:
            tasks = [self.add(m.imdb_mvid) for m in imdb]
            await asyncio.gather(*tasks)


async def main():
    adder = IMDbExtraAdder()
    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
