import sys
import asyncio
from datetime import datetime
from pathlib import Path

PROJ_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJ_DIR))

from backend.settings import settings
from database.manager import SourceDataModel, AbstractMovieDataSource
from services.countries import countries
from services.movie_genres import genres
from services.movie_types import movie_types
from services.imdb.dataset import IMDbDataSet
from services.imdb.scraper import IMDbScraper
from services.tmdb.scraper import TMDbScraper, MovieDoesNotExist, TMDbRequestError
from services.models import (
    IMDbMovieServiceDM,
    TMDbMovieServiceDM,
    CollectionServiceDM,
    ProductionServiceDM,
)


class CountrySourceDM(SourceDataModel):
    iso: str
    name_en: str
    name_ru: str
    image_url: str | None = None


class GenreSourceDM(SourceDataModel):
    name_en: str
    name_ru: str | None

    slug: str | None = None
    tmdb_name: str | None = None
    image_url: str | None = None


class MovieTypeSourceDM(SourceDataModel):
    name_en: str
    name_ru: str
    imdb_name: str

    @property
    def to_exclude(self) -> list[str]:
        return ["imdb_name"]


class CollectionSourceDM(SourceDataModel):
    tmdb_id: int

    name_en: str
    name_ru: str | None = None
    image_url: str | None = None


class ProductionSourceDM(SourceDataModel):
    tmdb_id: int

    name_en: str
    image_url: str | None
    country: CountrySourceDM | None = None

    ## will be setuped later
    slug: str | None = None

    @property
    def to_exclude(self) -> list[str]:
        return ["country", "slug"]


class TMDbMovieSourceDM(SourceDataModel):
    imdb_mvid: str
    tmdb_mvid: int

    release_date: datetime | None
    budget: int | None
    revenue: int | None
    image_url: str | None

    tagline_en: str | None
    overview_en: str | None

    tagline_ru: str | None
    overview_ru: str | None

    rate: float | None
    votes: int | None
    popularity: float | None

    ## need to prepare
    collection: CollectionSourceDM | None
    genres: list[GenreSourceDM] | None
    productions: list[ProductionSourceDM] | None
    countries: list[CountrySourceDM] | None

    @property
    def to_exclude(self) -> list[str]:
        return [
            "imdb_mvid",
            "collection",
            "genres",
            "productions",
            "countries",
        ]


class IMDbMovieSourceDM(SourceDataModel):
    imdb_mvid: str
    name_en: str
    name_ru: str | None = None

    is_adult: bool
    runtime: int | None = None

    rate: float | None = None
    wrate: float | None = None
    votes: int | None = None

    start_year: int
    end_year: int | None = None

    ## need to prepare
    movie_type: MovieTypeSourceDM
    genres: list[GenreSourceDM] = []

    ## will be setuped later
    slug: str | None = None

    @property
    def to_exclude(self) -> list[str]:
        return ["movie_type", "genres", "slug"]


class IMDbMovieExtraInfoSourceDM(SourceDataModel):
    imdb_mvid: str
    image_url: str | None = None

    error: str | None = None

    @property
    def to_exclude(self) -> list[str]:
        return ["error"]


class MovieDataSource(AbstractMovieDataSource):
    __instance = None

    def __new__(cls) -> "MovieDataSource":
        if cls.__instance is None:
            cls.__instance = super(MovieDataSource, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        self.imdb_ds = IMDbDataSet(debug=True)
        self.imdb_scraper = IMDbScraper()
        self.tmdb_scraper = TMDbScraper(
            api_key=settings.TMDB_APIKEY,
            proxy=settings.PROXY,
        )

        self.imdb_genres = {g.name_en: g for g in self.get_genres()}
        self.tmdb_genres = {g.tmdb_name: g for g in self.get_genres()}
        self.countries = {c.iso: c for c in self.get_countries()}
        self.movie_types = {mt.imdb_name: mt for mt in self.get_movie_types()}

    def get_countries(self) -> list[CountrySourceDM]:
        return [
            CountrySourceDM(
                iso=c.iso,
                name_en=c.name_en,
                name_ru=c.name_ru,
            )
            for c in countries
        ]

    def get_genres(self) -> list[GenreSourceDM]:
        return [
            GenreSourceDM(
                name_en=g.name_en,
                name_ru=g.name_ru,
                tmdb_name=g.tmdb_name,
                slug=g.slug,
            )
            for g in genres
        ]

    def get_movie_types(self) -> list[MovieTypeSourceDM]:
        return [
            MovieTypeSourceDM(
                name_en=mt.name_en,
                name_ru=mt.name_ru,
                imdb_name=mt.imdb_name,
            )
            for mt in movie_types
        ]

    async def get_imdb_movies(self, amount: int) -> list[IMDbMovieSourceDM]:
        return [self.prepare_imdb(m) for m in self.imdb_ds.get_movies(amount)]

    async def get_tmdb_movie(self, imdb_mvid: str) -> TMDbMovieSourceDM | None:
        try:
            return self.prepare_tmdb(await self.tmdb_scraper.get_movie(imdb_mvid))

        except MovieDoesNotExist as ex:
            print(ex)

        except TMDbRequestError as ex:
            print(ex)

    async def get_imdb_movie_extra(
        self, imdb_mvid: str
    ) -> IMDbMovieExtraInfoSourceDM | None:
        extra = await self.imdb_scraper.get_movie(imdb_mvid)
        return IMDbMovieExtraInfoSourceDM(
            imdb_mvid=extra.imdb_mvid,
            image_url=extra.image_url,
            error=extra.error,
        )

    def prepare_imdb(self, movie_svc: IMDbMovieServiceDM) -> IMDbMovieSourceDM:
        movie_type = self.movie_types.get(movie_svc.type, None)
        movie_genres = [self.imdb_genres.get(mg, None) for mg in movie_svc.genres]
        movie_genres = [mg for mg in movie_genres if mg is not None]
        return IMDbMovieSourceDM(
            imdb_mvid=movie_svc.imdb_mvid,
            name_en=movie_svc.name_en,
            name_ru=movie_svc.name_ru,
            is_adult=movie_svc.is_adult,
            runtime=movie_svc.runtime,
            rate=movie_svc.rate,
            wrate=movie_svc.wrate,
            votes=movie_svc.votes,
            start_year=movie_svc.start_year,
            end_year=movie_svc.end_year,
            movie_type=movie_type,
            genres=movie_genres,
        )

    def prepare_collection(
        self,
        collection_svc: CollectionServiceDM,
    ) -> CollectionSourceDM:
        if collection_svc:
            return CollectionSourceDM(
                tmdb_id=collection_svc.tmdb_id,
                name_en=collection_svc.name_en,
                name_ru=collection_svc.name_ru,
            )

    def prepare_production(
        self,
        production_svc: ProductionServiceDM,
    ) -> list[ProductionSourceDM]:
        if production_svc:
            return ProductionSourceDM(
                tmdb_id=production_svc.tmdb_id,
                name_en=production_svc.name_en,
                image_url=production_svc.image_url,
                country=self.countries.get(production_svc.country, None),
            )

    def prepare_tmdb(self, movie_svc: TMDbMovieServiceDM) -> TMDbMovieSourceDM:
        movie_genres = []
        if movie_svc.genres:
            movie_genres = [self.tmdb_genres.get(mg, None) for mg in movie_svc.genres]
            movie_genres = [mg for mg in movie_genres if mg is not None]

        movie_countries = []
        if movie_svc.countries:
            movie_countries = [self.countries.get(c, None) for c in movie_svc.countries]
            movie_countries = [mc for mc in movie_countries if mc is not None]

        collection = self.prepare_collection(movie_svc.collection)
        productions = []
        if movie_svc.productions:
            productions = [self.prepare_production(p) for p in movie_svc.productions]

        return TMDbMovieSourceDM(
            imdb_mvid=movie_svc.imdb_mvid,
            tmdb_mvid=movie_svc.tmdb_mvid,
            release_date=movie_svc.release_date,
            budget=movie_svc.budget,
            revenue=movie_svc.revenue,
            image_url=movie_svc.image_url,
            tagline_en=movie_svc.tagline_en,
            overview_en=movie_svc.overview_en,
            tagline_ru=movie_svc.tagline_ru,
            overview_ru=movie_svc.overview_ru,
            rate=movie_svc.rate,
            votes=movie_svc.votes,
            popularity=movie_svc.popularity,
            collection=collection,
            productions=productions,
            genres=movie_genres,
            countries=movie_countries,
        )


async def test():
    movie_ds = MovieDataSource()

    countries = movie_ds.get_countries()
    genres = movie_ds.get_genres()
    movie_types = movie_ds.get_movie_types()

    imdb_movies = await movie_ds.get_imdb_movies(1000)
    imdb_movie = imdb_movies[0]

    tmdb_movie = await movie_ds.get_tmdb_movie(imdb_movie.imdb_mvid)
    imdb_extra = await movie_ds.get_imdb_movie_extra(imdb_movie.imdb_mvid)


# if __name__ == "__main__":
#     asyncio.run(test())
