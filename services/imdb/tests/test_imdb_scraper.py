import sys
from pathlib import Path

import pytest

PROJ_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJ_DIR))

from services.imdb.scraper import IMDbScraper, IMDb404Error


class TestCase:
    imdb_mvid = "tt0133093"
    tmdb_mvid = 603

    imdb_not_existing = "tt011234"


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
        movie = await scraper.get_movie(TestCase.imdb_mvid)

        assert movie.imdb_mvid == TestCase.imdb_mvid
        assert movie.error is None
        assert movie.image_url.startswith("https://")

    @pytest.mark.asyncio
    async def test_get_not_existing_movie(self):
        scraper = self.get_scraper()

        error = None
        try:
            movie = await scraper.get_movie(TestCase.imdb_not_existing)
        except IMDb404Error as exc:
            error = exc

        assert isinstance(error, IMDb404Error)
