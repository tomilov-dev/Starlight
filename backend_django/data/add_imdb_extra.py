import os
import sys
import asyncio
import django
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio

PROJ_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJ_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starlight_backend.settings")
django.setup()

from movies.models import IMDb
from services.imdb.scraper import (
    IMDbScraper,
    IMDbMovieExtraInfo,
    IMDb404Error,
    IMDb503Error,
    IMDbEmptyResponeError,
)


class IMDbExtraInfoAdder(object):
    def __init__(self, scraper: IMDbScraper) -> None:
        self._scraper = scraper

    async def get_movie(self, imdb_mvid: str) -> IMDbMovieExtraInfo:
        return await self._scraper.get_movie(imdb_mvid)

    async def mark_up(self, imdb: IMDb):
        imdb.imdb_extra_added = True
        await imdb.asave()

    async def add_image_url(self, imdb: IMDb, movie: IMDbMovieExtraInfo):
        if movie.image_url:
            if not imdb.image_url:
                imdb.image_url = movie.image_url
                await imdb.asave()

    async def add(self, imdb: IMDb) -> None:
        try:
            imdb_mvid = imdb.imdb_mvid
            movie = await self.get_movie(imdb_mvid)

            if movie:
                await self.add_image_url(imdb, movie)

            await self.mark_up(imdb)

        except IMDbEmptyResponeError:
            pass

        except IMDb404Error:
            pass

        except IMDb503Error:
            pass

    async def add_all(self) -> None:
        print("Collect movies without imdb_extra_added mark")
        movies = IMDb.objects.filter(imdb_extra_added=False)

        print("Add IMDb extra info")
        tasks = [asyncio.create_task(self.add(movie)) async for movie in movies]
        await tqdm_asyncio.gather(*tasks, total=len(tasks))


async def main():
    scraper = IMDbScraper(None, None, 10, 1)
    adder = IMDbExtraInfoAdder(scraper)

    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
