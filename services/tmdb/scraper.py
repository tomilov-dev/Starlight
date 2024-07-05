import sys
from pathlib import Path
from typing import Any
from pprint import pprint
from datetime import datetime
from abc import abstractmethod

from pydantic import BaseModel
from aiohttp import ClientResponse

sys.path.append(str(Path(__file__).parent.parent.parent))
from services.tmdb.notation import MovieDetails as MD
from services.models import TMDbMovieServiceDM, CollectionServiceDM, ProductionServiceDM
from services.base_scraper import BaseScraper
from services.tmdb.settings import settings


class TMDbAuthFailed(Exception):
    pass


class TMDbInvalidID(Exception):
    pass


class TMDbOverLimit(Exception):
    pass


class MovieDoesNotExist(Exception):
    pass


class TMDbRequestError(Exception):
    pass


class AbstractFactory:
    @abstractmethod
    def create(self, **kwargs: dict[str, Any]) -> BaseModel:
        pass


class CollectionFactory(AbstractFactory):
    def add_name(
        self,
        collection: CollectionServiceDM,
        name: str,
        lang: str,
    ) -> None:
        name_en = collection.name_en
        name_ru = collection.name_ru

        if lang == "en-US":
            name_en = name
        elif lang == "ru":
            name_ru = name

        collection.name_en = name_en
        collection.name_ru = name_ru

    def create(
        self,
        tmdb_id: int,
        name: str,
        lang: str,
    ) -> CollectionServiceDM:
        name_ru = None
        name_en = None

        if lang == "en-US":
            name_en = name
        elif lang == "ru":
            name_ru = name

        return CollectionServiceDM(
            tmdb_id=tmdb_id,
            name_en=name_en,
            name_ru=name_ru,
        )


class ProductionFactory(AbstractFactory):
    def create(
        self,
        tmdb_id: int,
        name_en: str,
        country: str,
        image_url: str,
    ) -> ProductionServiceDM:
        return ProductionServiceDM(
            tmdb_id=tmdb_id,
            name_en=name_en,
            country=country,
            image_url=image_url,
        )


class TMDbMovieFactory(AbstractFactory):
    def __init__(self) -> None:
        self.collection_factory = CollectionFactory()
        self.production_factory = ProductionFactory()

    def create(self, **kwargs: dict[str, Any]) -> TMDbMovieServiceDM | None:
        try:
            return TMDbMovieServiceDM(
                name_en=kwargs.get(MD.TITLE, None),
                tmdb_mvid=self.cast(self.get(MD.TMDB_MVID, **kwargs), int),
                imdb_mvid=self.get(MD.IMDB_MVID, **kwargs),
                image_url=self.image(self.get(MD.IMAGE_URL, **kwargs)),
                tagline_en=self.get(MD.TAGLINE, **kwargs),
                overview_en=self.get(MD.OVERVIEW, **kwargs),
                release_date=self.get_release_date(**kwargs),
                budget=self.zero_to_none(self.cast(self.get(MD.BUDGET, **kwargs), int)),
                revenue=self.zero_to_none(
                    self.cast(self.get(MD.REVENUE, **kwargs), int)
                ),
                rate=self.zero_to_none(self.cast(self.get(MD.RATE, **kwargs), float)),
                votes=self.zero_to_none(self.cast(self.get(MD.VOTES, **kwargs), int)),
                popularity=self.cast(self.get(MD.POPULARITY, **kwargs), float),
                collection=self.get_collection(**kwargs),
                countries=self.get_countries(**kwargs),
                productions=self.get_productions(**kwargs),
                genres=self.get_genres(**kwargs),
                title_ru=None,
                tagline_ru=None,
                overview_ru=None,
            )

        except Exception as ex:
            print(ex)

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
    ) -> CollectionServiceDM | None:
        collection = None
        data: dict = self.get(MD.COLLECTION, **kwargs)
        if data:
            try:
                collection = self.collection_factory.create(
                    tmdb_id=self.get(MD.COLLECTION_ID, **data),
                    name=self.get(MD.COLLECTION_NAME, **data),
                    lang=lang,
                )
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

    def get_productions(self, **kwargs) -> list[ProductionServiceDM] | None:
        productions = None

        production_data = self.get(MD.PRODUCTION, **kwargs)
        if production_data:
            try:
                productions = []
                for data in production_data:
                    data: dict

                    production = self.production_factory.create(
                        tmdb_id=self.cast(self.get(MD.PRODUCTION_ID, **data), int),
                        name_en=self.get(MD.PRODUCTION_NAME, **data),
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

    def add_ru_details(
        self,
        movie: TMDbMovieServiceDM,
        **kwargs,
    ) -> TMDbMovieServiceDM:
        movie.name_ru = kwargs.get(MD.TITLE, None)
        movie.tagline_ru = kwargs.get(MD.TAGLINE, None)
        movie.overview_ru = kwargs.get(MD.OVERVIEW, None)

        collection = kwargs.get(MD.COLLECTION, None)
        if collection:
            collection_name = collection.get(MD.COLLECTION_NAME, None)

            self.collection_factory.add_name(
                movie.collection,
                collection_name,
                "ru",
            )


class TMDbScraper(BaseScraper):
    """Recommended limit is 40r/1s because of API limits"""

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
        max_rate: int = settings.TMDB_MAX_RATE,
        rate_period: int = settings.TMDB_RATE_PERIOD,
        debug: bool = False,
    ) -> None:
        super().__init__(
            proxy,
            max_rate,
            rate_period,
            debug,
        )

        self.api_key = api_key
        self.update_headers("Authorization", f"Bearer {api_key}")

        self.movie_factory = TMDbMovieFactory()

    @property
    def custom_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US",
        }

    def check_status(self, status: int) -> None:
        error = self.STATUSES.get(status, None)
        if error is not None:
            raise error

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

    async def get_movie(self, imdb_mvid: str) -> TMDbMovieServiceDM | None:
        id_search = await self.find_by_imdb_id(imdb_mvid)

        if "movie_results" not in id_search:
            raise TMDbRequestError(f"Error in TMDb search by id request: {imdb_mvid}")

        movies = id_search["movie_results"]
        if not movies:
            raise MovieDoesNotExist(f"Movie with IMDb id {imdb_mvid} doesn't exist")

        tmdb_mvid = movies[0]["id"]
        en_movie_details = await self.get_movie_details(tmdb_mvid)
        movie = self.movie_factory.create(**en_movie_details)

        if not movie:
            raise TMDbRequestError(f"Error int TMDb movie details request: {tmdb_mvid}")

        ru_movie_details = await self.get_movie_details(tmdb_mvid, "ru")
        self.movie_factory.add_ru_details(movie, **ru_movie_details)

        return movie
