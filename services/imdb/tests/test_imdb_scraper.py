import sys
import asyncio
from pathlib import Path

import pytest

PROJ_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJ_DIR))

from services.imdb.scraper import IMDbScraper, IMDbMovieExtraInfo


class TestCase:
    imdb_mvid = "tt0133093"
    tmdb_mvid = 603


class TestIMDbScraper:
    def get_scraper(self) -> IMDbScraper:
        scraper = IMDbScraper(
            max_rate=10,
            rate_period=1,
        )
        return scraper

    @pytest.mark.asyncio
    async def test_get_movie(self):
        scraper = self.get_scraper()
        movie: IMDbMovieExtraInfo = await scraper.get_movie(TestCase.imdb_mvid)

        assert movie.imdb_mvid == TestCase.imdb_mvid
        assert movie.image_url.startswith("https://")


async def hand_test():
    test = TestIMDbScraper()
    await test.test_get_movie()


if __name__ == "__main__":
    asyncio.run(hand_test())
