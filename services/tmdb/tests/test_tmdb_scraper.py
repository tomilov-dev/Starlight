import sys
import asyncio
from pathlib import Path

import pytest

PROJ_DIR = Path(__file__).parent.parent.parent.parent
sys.path.append(str(PROJ_DIR))

from services.tmdb.scraper import TMDbScraper, TMDbMovie
from services.tmdb.settings import settings


PROXY = settings.TEST_PROXY


class TestCase:
    imdb_mvid = "tt0133093"
    tmdb_mvid = 603

    original_title = "The Matrix"
    tagline_en = "Believe the unbelievable."
    collection = "The Matrix Collection"

    title_ru = "Матрица"
    tagline_ru = "Мир Матрицы — это иллюзия"
    collection_ru = "Матрица (Коллекция)"


class TestTMDbScraper:
    def get_scraper(self) -> TMDbScraper:
        return TMDbScraper(
            settings.APIKEY,
            proxy=PROXY,
            max_rate=45,
            rate_period=1,
        )

    @pytest.mark.asyncio
    async def test_find_by_imdb_id(self):
        scraper = self.get_scraper()
        data = await scraper.find_by_imdb_id(TestCase.imdb_mvid)

        id = data["movie_results"][0]["id"]
        title = data["movie_results"][0]["original_title"]

        assert id == TestCase.tmdb_mvid
        assert title == TestCase.original_title

    @pytest.mark.asyncio
    async def test_get_movie_details_en(self):
        scraper = self.get_scraper()
        data = await scraper.get_movie_details(TestCase.imdb_mvid)

        tmdb_mvid = data["id"]
        imdb_mvid = data["imdb_id"]
        title = data["title"]
        tagline = data["tagline"]
        collection = data["belongs_to_collection"]["name"]

        assert imdb_mvid == TestCase.imdb_mvid
        assert tmdb_mvid == TestCase.tmdb_mvid
        assert title == TestCase.original_title
        assert tagline == TestCase.tagline_en
        assert collection == TestCase.collection

    @pytest.mark.asyncio
    async def test_get_movie_details_ru(self):
        scraper = self.get_scraper()
        data = await scraper.get_movie_details(TestCase.imdb_mvid, lang="ru")

        tmdb_mvid = data["id"]
        imdb_mvid = data["imdb_id"]
        title = data["title"]
        tagline = data["tagline"]
        collection = data["belongs_to_collection"]["name"]

        assert imdb_mvid == TestCase.imdb_mvid
        assert tmdb_mvid == TestCase.tmdb_mvid
        assert title == TestCase.title_ru
        assert tagline == TestCase.tagline_ru
        assert collection == TestCase.collection_ru

    @pytest.mark.asyncio
    async def test_get_movie(self):
        scraper = self.get_scraper()
        movie: TMDbMovie = await scraper.get_movie(TestCase.imdb_mvid)

        assert movie.imdb_mvid == TestCase.imdb_mvid
        assert movie.tmdb_mvid == TestCase.tmdb_mvid
        assert movie.tagline_en == TestCase.tagline_en
        assert movie.collection.name == TestCase.collection


async def hand_test():
    test = TestTMDbScraper()
    await test.test_get_movie_details_ru()


if __name__ == "__main__":
    asyncio.run(hand_test())
