import re
import sys
import asyncio
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup as soup
from tqdm.asyncio import tqdm_asyncio


PROJ_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJ_DIR))


from services.base_scraper import BaseScraper
from services.models import IMDbMovieExtraInfo


class IMDbEmptyResponeError(Exception):
    pass


class IMDb404Error(Exception):
    pass


class IMDb503Error(Exception):
    pass


class IMDbMovieExtraInfoInterface(object):
    imdb_mvid: str
    image_url: str

    error: bool


class IMDBMovieExtraInfoFactory:
    def create(self, **kwargs) -> IMDbMovieExtraInfo:
        self._error = self._check_error(**kwargs)
        return IMDbMovieExtraInfo(
            error=self._error,
            imdb_mvid=kwargs.get("imdb_mvid"),
            image_url=self._get("image_url", **kwargs),
        )

    def _get(self, key: str, **kwargs):
        data = None
        if not self._error:
            data = kwargs.get(key, None)
        return data

    def _check_error(self, **kwargs) -> bool:
        if "error" in kwargs:
            return kwargs.get("error")
        return None


class IMDbScraper(BaseScraper):
    """Recommended limit is 5r/1s and lower"""

    def __init__(
        self,
        proxy: str = None,
        max_rate: int = 5,
        rate_period: int = 1,
        debug: bool = False,
    ) -> None:
        super().__init__(
            proxy,
            max_rate,
            rate_period,
            debug,
        )

        self.factory = IMDBMovieExtraInfoFactory()

    @property
    def custom_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US",
        }

    async def extractor(self, response: aiohttp.ClientResponse):
        data = await response.text()
        return data

    def _parse_movie(self, movie_html: str, data: dict = {}) -> dict:
        s = soup(movie_html, "lxml")

        img = s.find("div", {"class": "ipc-media"})
        img = img.find("img").get("src")
        img = re.sub(r"\._V1_.*", ".jpg", img, flags=re.IGNORECASE)

        data["image_url"] = img

        return data

    def _check_response(self, movie_html: str, imdb_mvid: str) -> None:
        ERROR503 = "Error 503 - IMDb"
        ERROR404 = "404 Error - IMDb"

        if movie_html is None:
            raise IMDbEmptyResponeError(f"IMDbEmptyResponeError in Movie:", imdb_mvid)

        elif ERROR503 in movie_html:
            raise IMDb503Error(f"IMDb503Error in Movie:", imdb_mvid)

        elif ERROR404 in movie_html:
            raise IMDb404Error(f"IMDb404Error in Movie:", imdb_mvid)

        return False

    async def get_movie(self, imdb_mvid: str) -> IMDbMovieExtraInfo:
        movie_data = {"imdb_mvid": imdb_mvid}
        URL = f"https://www.imdb.com/title/{imdb_mvid}"

        movie_html = await self.request(URL)
        self._check_response(movie_html, imdb_mvid)

        movie_data = self._parse_movie(movie_html, movie_data)
        return self.factory.create(**movie_data)


async def LoadTesting():
    scraper = IMDbScraper(
        max_rate=5,
        rate_period=1,
    )

    tasks = [asyncio.create_task(scraper.get_movie("tt0078748")) for _ in range(10000)]
    moviesInfo = await tqdm_asyncio.gather(*tasks)

    for movieInfo in moviesInfo:
        movieInfo: IMDbMovieExtraInfo

        print(movieInfo.image_url)


if __name__ == "__main__":
    asyncio.run(LoadTesting())
