import re
from pathlib import Path
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup as soup


PROJ_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJ_DIR))


from services.base_scraper import BaseScraper


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


class IMDbMovieExtraInfo(IMDbMovieExtraInfoInterface):
    def __init__(self, **kwargs) -> None:
        self._error = self._check_error(**kwargs)
        self.imdb_mvid = kwargs.get("imdb_mvid")

        # if error in response: return None
        self.image_url = self._get("image_url", **kwargs)

    def _get(self, key: str, **kwargs):
        data = None
        if not self._error:
            data = kwargs.get(key, None)
        return data

    def _check_error(self, **kwargs) -> bool:
        if "error" in kwargs:
            return kwargs.get("error")
        return None

    @property
    def error(self) -> bool:
        return self._error is not None

    def __str__(self) -> str:
        return self.imdb_mvid


class IMDbScraper(BaseScraper):
    """Recommended limit is 10r/1s and lower"""

    BASE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "accept": "text/html",
        "accept-language": "en-US",
    }

    def __init__(
        self,
        api_key: str = None,
        proxy: str = None,
        max_rate: int = 49,
        rate_period: int = 1,
        debug: bool = False,
    ) -> None:
        super().__init__(
            api_key,
            proxy,
            max_rate,
            rate_period,
            debug,
        )

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
        return IMDbMovieExtraInfo(**movie_data)


async def test():
    scraper = IMDbScraper(
        max_rate=10,
        rate_period=1,
    )

    tasks = [asyncio.create_task(scraper.get_movie("tt0078748")) for _ in range(1)]
    moviesInfo = await asyncio.gather(*tasks)

    for movieInfo in moviesInfo:
        movieInfo: IMDbMovieExtraInfo

        print(movieInfo.image_url)


if __name__ == "__main__":
    asyncio.run(test())
