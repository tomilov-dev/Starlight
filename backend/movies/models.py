import sys
from pathlib import Path

from pydantic import BaseModel
from datetime import datetime


sys.path.append(str(Path(__file__).parent.parent))
from movies.base_models import IMDbMovieBaseDTO
from persons.models import MoviePrincipalPersonDTO


class MovieCollectionDTO(BaseModel):
    id: int
    tmdb_id: int

    name_en: str
    name_ru: str | None
    image_url: str | None

    ## Relations

    ## not in use
    # tmdb_movies: list["TMDbMovieDTO"] = []


class TMDbMovieDTO(BaseModel):
    id: int
    tmdb_mvid: int

    release_date: datetime
    budget: int | None = None
    revenue: int | None = None
    image_url: str | None = None

    tagline_en: str | None = None
    overview_en: str | None = None

    tagline_ru: str | None = None
    overview_ru: str | None = None

    rate: float | None = None
    votes: int | None = None
    popularity: float | None = None

    ## Relations
    collection: MovieCollectionDTO | None = None

    ## not in use
    # imdb: IMDbMovieBaseDTO | None = None
    # countries: list["MovieCountryDTO"] = []
    # production_companies: list["MovieProductionDTO"] = []


class CountryDTO(BaseModel):
    id: int

    iso: str
    name_en: str
    name_ru: str | None = None
    image_url: str | None = None

    ## Relations

    ## not in use
    # movies: list["MovieCountryDTO"] = []
    # productions: list["ProductionCompanyDTO"] = []


class MovieCountryDTO(BaseModel):
    id: int

    ## Relations
    country: CountryDTO

    ## not in use
    # imdb_movie: IMDbMovieBaseDTO
    # tmdb_movie: TMDbMovieDTO
    # country: CountryDTO


class ProductionCompanyDTO(BaseModel):
    id: int
    tmdb_id: int

    name_en: str
    slug: str
    image_url: str | None = None

    ## Relations
    country_origin: CountryDTO | None = None

    ## not in use
    # movies: list["MovieProductionDTO"] = []


class MovieProductionDTO(BaseModel):
    id: int

    ## Relations
    production_company: ProductionCompanyDTO

    ## not in use
    # imdb_movie: IMDbMovieBaseDTO
    # tmdb_movie: TMDbMovieDTO
    # production_company: ProductionCompanyDTO


class GenreDTO(BaseModel):
    id: int
    name_en: str
    name_ru: str | None = None

    slug: str
    tmdb_name: str | None = None
    image_url: str | None = None

    ## Relations

    ## not in use
    # movies: list["MovieGenreDTO"] = []


class MovieGenreGTO(BaseModel):
    id: int

    ## Relations
    genre: "GenreDTO"

    ## not in use
    # imdb_movie: IMDbMovieBaseDTO


class IMDbMovieExtendedDTO(IMDbMovieBaseDTO):
    tmdb: TMDbMovieDTO | None = None

    genres: list[MovieGenreGTO] = []
    countries: list[MovieCountryDTO] = []
    production_companies: list[MovieProductionDTO] = []
    principals: list[MoviePrincipalPersonDTO] = []
