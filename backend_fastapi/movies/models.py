from pydantic import BaseModel
from datetime import datetime


class IMDbDTO(BaseModel):
    imdb_mvid: str
    type: str

    title_en: str
    title_ru: str | None
    slug: str

    is_adult: bool
    runtime: int

    rate: float | None
    wrate: float | None
    votes: int | None

    imdb_extra_added: bool
    tmdb_added: bool
    image_url: str | None


class CollectionDTO(BaseModel):
    id: int
    name_en: str
    name_ru: str | None


class TMDbDTO(BaseModel):
    tmdb_mvid: int
    imdb_mvid: str
    collection: int

    release_date: datetime
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


class CountryDTO(BaseModel):
    name_en: str
    name_ru: str | None


class MovieCountryDTO(BaseModel):
    id: int
    country: str
    imdb_mvid: str
    tmdb_mvid: str


class ProductionCompanyDTO(BaseModel):
    company: int

    name: str
    country: str | None
    image_url: str | None


class MovieProductionDTO(BaseModel):
    id: int
    company: int
    imdb_mvid: str
    tmdb_mvid: int


class GenreDTO(BaseModel):
    id: int
    imdb_name: str
    slug: str

    tmdb_name: str | None
    name_ru: str | None


class MovieGenreDTO(BaseModel):
    id: int
    imdb_mvid: str
    genre: int
