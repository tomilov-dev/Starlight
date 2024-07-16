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


class CountryServiceDM(
    NameMixin,
):
    iso: str


class GenreServiceDM(
    SlugMixin,
    NameMixin,
):
    tmdb_name: str | None


class ContentTypeServiceDM(
    NameMixin,
):
    imdb_name: str


class PersonProfessionServiceDM(NameMixin):
    imdb_name: str
    crew: bool = False


class IMDbMovieServiceDM(
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


class IMDbPersonServiceDM(
    InitSlugMixin,
    NameMixin,
):
    imdb_nmid: str

    birth_y: int | None = None
    death_y: int | None = None
    professions: list[str] | None = None
    known_for_titles: list[str] | None = None


class IMDbPrincipalServiceDM(BaseModel):
    imdb_movie: str
    imdb_person: str
    ordering: int

    # category :: profession category (profession)
    category: str | None = None
    job: str | None = None
    characters: list[str] | None = None


class CollectionServiceDM(BaseModel):
    tmdb_id: int
    name_en: str | None = None
    name_ru: str | None = None


class ProductionServiceDM(
    InitSlugMixin,
    NameMixin,
):
    tmdb_id: int
    country: str | None
    image_url: str | None


class TMDbMovieServiceDM(
    InitSlugMixin,
    NameMixin,
):
    imdb_mvid: str
    tmdb_mvid: int

    image_url: str
    tagline_en: str | None = None
    overview_en: str | None = None

    release_date: datetime
    budget: int | None = None
    revenue: int | None = None

    rate: float | None = None
    votes: int | None = None
    popularity: float | None = None

    genres: list[str] | None
    countries: list[str] | None
    collection: CollectionServiceDM | None
    productions: list[ProductionServiceDM] | None

    tagline_ru: str | None = None
    overview_ru: str | None = None


class IMDbMovieExtraInfoServiceDM(BaseModel):
    imdb_mvid: str
    image_url: str

    error: str | None
