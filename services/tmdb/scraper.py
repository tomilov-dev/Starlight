import sys
import asyncio
from pathlib import Path
from pprint import pprint
from datetime import datetime

from aiohttp import ClientResponse


PROJ_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJ_DIR))

from services.base_scraper import BaseScraper
from services.tmdb.notation import MovieDetails as MD


class TMDbAuthFailed(Exception):
    pass


class TMDbInvalidID(Exception):
    pass


class TMDbOverLimit(Exception):
    pass


class MovieDoesNotExist(Exception):
    pass


class Collection(object):
    id: int
    name_en: str
    name_ru: str

    def __init__(
        self,
        id: int,
        name_en: str | None = None,
        name_ru: str | None = None,
    ) -> None:
        self.id = id
        self.name_en = name_en
        self.name_ru = name_ru

    def set_name(self, name: str, lang: str) -> None:
        if lang == "en-US":
            self.name_en = name
        elif lang == "ru":
            self.name_ru = name
        else:
            raise ValueError("Unidentified language")

    def __repr__(self) -> str:
        return self.name_en


class Production(object):
    id: int
    name: str
    country: str
    image_url: str

    def __init__(
        self,
        id: int,
        name: str,
        country: str,
        image_url: str,
    ) -> None:
        self.id = id
        self.name = name
        self.country = country
        self.image_url = image_url

    def __hash__(self) -> str:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Production):
            return False
        return self.__hash__() == other.__hash__()

    def __repr__(self) -> str:
        return f"{self.name}"


class TMDbMovieIntefrace(object):
    imdb_mvid: str
    tmdb_mvid: int

    image_url: str
    tagline_en: str
    overview_en: str

    release_date: datetime
    budget: int
    revenue: int

    rate: float
    votes: int
    popularity: int

    collection: Collection | None
    genres: list[str] | None
    productions: list[Production] | None
    countries: list[str] | None

    title_ru: str
    tagline_ru: str
    overview_ru: str


class TMDbMovie(TMDbMovieIntefrace):
    def __init__(self, **kwargs) -> None:
        self.tmdb_mvid = self.cast(self.get(MD.TMDB_MVID, **kwargs), int)
        self.imdb_mvid = self.get(MD.IMDB_MVID, **kwargs)

        self.image_url = self.image(self.get(MD.IMAGE_URL, **kwargs))
        self.tagline_en = self.get(MD.TAGLINE, **kwargs)
        self.overview_en = self.get(MD.OVERVIEW, **kwargs)

        self.release_date = self.get_release_date(**kwargs)
        self.budget = self.zero_to_none(self.cast(self.get(MD.BUDGET, **kwargs), int))
        self.revenue = self.zero_to_none(self.cast(self.get(MD.REVENUE, **kwargs), int))

        self.rate = self.zero_to_none(self.cast(self.get(MD.RATE, **kwargs), float))
        self.votes = self.zero_to_none(self.cast(self.get(MD.VOTES, **kwargs), int))
        self.popularity = self.cast(self.get(MD.POPULARITY, **kwargs), float)

        self.collection = self.get_collection(**kwargs)
        self.countries = self.get_countries(**kwargs)
        self.productions = self.get_productions(**kwargs)
        self.genres = self.get_genres(**kwargs)

        self.title_ru = None
        self.tagline_ru = None
        self.overview_ru = None

    def image(self, path: str | None) -> str | None:
        if path:
            path = "https://image.tmdb.org/t/p/w500" + path
        return path

    def get(self, attr, **kwargs):
        data = kwargs.get(attr, None)
        if data == "":
            data = None
        return data

    def zero_to_none(self, value):
        if value == 0:
            value = None
        return value

    def cast(self, value, to_type):
        if value is not None:
            value = to_type(value)
        return value

    def get_release_date(self, **kwargs) -> datetime | None:
        release_date = self.get(MD.RELEASE_DATE, **kwargs)
        if release_date:
            try:
                release_date = datetime.strptime(release_date, "%Y-%m-%d")
            except Exception as ex:
                release_date = None
                print(ex)

        return release_date

    def get_collection(
        self,
        lang: str = "en-US",
        **kwargs,
    ) -> Collection | None:
        collection = None
        data: dict = self.get(MD.COLLECTION, **kwargs)
        if data:
            try:
                name = self.get(MD.COLLECTION_NAME, **data)
                collection = Collection(
                    id=self.get(MD.COLLECTION_ID, **data),
                )
                collection.set_name(name, lang)
            except Exception as ex:
                collection = None
                print(ex)

        return collection

    def get_countries(self, **kwargs) -> list[str] | None:
        countries = None

        countries_data = self.get(MD.COUNTRIES, **kwargs)
        if countries_data:
            try:
                countries: list[str] = []
                for data in countries_data:
                    data: dict
                    country = data.get(MD.COUNTRY_ISO, None)
                    if country:
                        countries.append(country)

            except Exception as ex:
                countries = None
                print(ex)

        return countries

    def get_productions(self, **kwargs) -> list[Production] | None:
        productions = None

        production_data = self.get(MD.PRODUCTION, **kwargs)
        if production_data:
            try:
                productions = []
                for data in production_data:
                    data: dict

                    production = Production(
                        id=self.cast(self.get(MD.PRODUCTION_ID, **data), int),
                        name=self.get(MD.PRODUCTION_NAME, **data),
                        country=self.get(MD.PRODUCTION_COUNTRY, **data),
                        image_url=self.image(self.get(MD.PRODUCTION_IMAGE_URL, **data)),
                    )

                    productions.append(production)
            except Exception as ex:
                productions = None
                print(ex)

        return productions

    def get_genres(self, **kwargs) -> list[str] | None:
        genres = None

        genres_data = kwargs.get(MD.GENRES, None)
        if genres_data:
            try:
                genres = []
                for data in genres_data:
                    data: dict
                    genre = self.get(MD.GENRE_NAME, **data)
                    if genre:
                        genres.append(genre)

            except Exception as ex:
                genres = None
                print(ex)

        return genres

    def add_ru_details(self, **kwargs) -> None:
        self.title_ru = self.get(MD.TITLE, **kwargs)
        self.tagline_ru = self.get(MD.TAGLINE, **kwargs)
        self.overview_ru = self.get(MD.OVERVIEW, **kwargs)

        ru_collection = self.get_collection(lang="ru", **kwargs)
        if ru_collection:
            self.collection.set_name(ru_collection.name_ru, "ru")

    def show_data(self) -> None:
        data = {
            "tmdb_mvid": self.tmdb_mvid,
            "imdb_mvid": self.imdb_mvid,
            "image_url": self.image_url,
            "tagline_en": self.tagline_en,
            "overview_en": self.overview_en,
            "release_date": self.release_date,
            "budget": self.budget,
            "revenue": self.revenue,
            "rate": self.rate,
            "votes": self.votes,
            "popularity": self.popularity,
            "collection": self.collection,
            "countries": self.countries,
            "productions": self.productions,
            "genres": self.genres,
            "title_ru": self.title_ru,
            "tagline_ru": self.tagline_ru,
            "overview_ru": self.overview_ru,
        }

        pprint(data)

    def __repr__(self) -> str:
        return self.imdb_mvid


class TMDbScraper(BaseScraper):
    """Recommended limit is 45req/1s because of API limits"""

    BASE_HEADERS = {"Content-Type": "application/json"}

    STATUSES = {
        200: None,
        401: TMDbAuthFailed,
        404: TMDbInvalidID,
        429: TMDbOverLimit,
    }

    def __init__(
        self,
        api_key: str,
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

    def check_status(self, status: int) -> None:
        error = self.STATUSES.get(status, None)
        if error is not None:
            raise error()

    async def extractor(self, response: ClientResponse):
        self.check_status(response.status)

        data = await response.json()
        return data

    async def find_by_imdb_id(self, imdb_mvid: str) -> dict:
        URL = f"https://api.themoviedb.org/3/find/{imdb_mvid}?external_source=imdb_id"
        return await self.request(URL)

    async def get_movie_details(
        self,
        tmdb_mvid: str | int,
        lang: str = "en-US",
    ) -> dict:
        URL = f"https://api.themoviedb.org/3/movie/{tmdb_mvid}?language={lang}"
        return await self.request(URL)

    async def get_movie(self, imdb_mvid: str) -> TMDbMovie:
        id_search = await self.find_by_imdb_id(imdb_mvid)
        movies = id_search["movie_results"]

        if not movies:
            raise MovieDoesNotExist(f"Movie with IMDb id {imdb_mvid} doesn't exist")

        tmdb_mvid = movies[0]["id"]
        en_movie_details = await self.get_movie_details(tmdb_mvid)
        movie = TMDbMovie(**en_movie_details)

        ru_movie_details = await self.get_movie_details(tmdb_mvid, "ru")
        movie.add_ru_details(**ru_movie_details)

        return movie


async def test():
    proxy = "38.170.252.236:9662@JQ7suq:TA3vLt"
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZWIzNGQxNGJhZWEwM2JiZjRmYTVhZTkzNTdjYTllZSIsInN1YiI6IjY1YWQzODIyMjVjZDg1MDBlYTBjYjgzMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.o7Q5t7MZiKC3SnXs2vYmdGSY6HWMg4PZdYcSMANKOSc"

    scraper = TMDbScraper(api_key, proxy)

    # movie = await scraper.get_movie("tt000")  ## Non-existent movie
    movie = await scraper.get_movie("tt0133093")  ## Matrix
    # movie = await scraper.get_movie("tt9911774")
    # movie = await scraper.get_movie("tt9911196")
    # movie = await scraper.get_movie("tt0133021")

    print(movie)
    print(movie.tagline_ru)
    print(movie.tagline_en)

    movie.show_data()


async def main():
    proxy = "38.170.252.236:9662@JQ7suq:TA3vLt"
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZWIzNGQxNGJhZWEwM2JiZjRmYTVhZTkzNTdjYTllZSIsInN1YiI6IjY1YWQzODIyMjVjZDg1MDBlYTBjYjgzMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.o7Q5t7MZiKC3SnXs2vYmdGSY6HWMg4PZdYcSMANKOSc"

    scraper = TMDbScraper(api_key, proxy, 45, 1, True)

    tasks = [asyncio.create_task(scraper.get_movie("tt0133093")) for _ in range(500)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(test())
