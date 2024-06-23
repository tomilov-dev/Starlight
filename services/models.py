"""Service Data Models SDM - for input data to Database"""

from pydantic import BaseModel
from datetime import datetime


class NameMixin(BaseModel):
    name_en: str
    name_ru: str | None = None


class SlugMixin(BaseModel):
    slug: str | None = None


class InitSlugMixin(BaseModel):
    init_slug: str | None = None

    def set_init_slug(self, slug: str) -> None:
        self.init_slug = slug


class CountrySDM(
    NameMixin,
):
    iso: str


class GenreSDM(
    SlugMixin,
    NameMixin,
):
    tmdb_name: str | None


class MovieTypeSDM(
    NameMixin,
):
    imdb_name: str


class PersonProfessionSDM(NameMixin):
    imdb_name: str
    crew: bool = False


class IMDbMovieSDM(
    InitSlugMixin,
    NameMixin,
):
    imdb_mvid: str
    type: str

    is_adult: bool
    runtime: int | None = None

    rate: float | None = None
    wrate: float | None = None
    votes: int | None = None

    genres: list[str] | None = None

    start_year: int
    end_year: int | None = None


class IMDbPersonSDM(
    InitSlugMixin,
    NameMixin,
):
    imdb_nmid: str

    birth_y: int | None = None
    death_y: int | None = None
    professions: list[str] | None = None
    # professions: list[PersonProfessionSDM] | None = None
    known_for_titles: list[str] | None = None


class IMDbPrincipalSDM(BaseModel):
    imdb_movie: str
    imdb_person: str
    ordering: int

    # category :: profession category (profession)
    category: str | None = None
    job: str | None = None
    characters: list[str] | None = None


class CollectionSDM(BaseModel):
    tmdb_id: int
    name_en: str | None = None
    name_ru: str | None = None


class ProductionSDM(
    InitSlugMixin,
    NameMixin,
):
    tmdb_id: int
    country: str | None
    image_url: str | None


class TMDbMovieSDM(
    InitSlugMixin,
    NameMixin,
):
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
    popularity: float

    collection: CollectionSDM | None
    genres: list[str] | None
    productions: list[ProductionSDM] | None
    countries: list[str] | None

    tagline_ru: str | None = None
    overview_ru: str | None = None


class IMDbMovieExtraInfo(BaseModel):
    imdb_mvid: str
    image_url: str

    error: str | None
