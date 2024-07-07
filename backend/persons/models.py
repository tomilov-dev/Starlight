import sys
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

sys.path.append(Path(__file__).parent.parent)
from movies.base_models import IMDbMovieBaseDTO


class IMDbPersonDTOBase(BaseModel):
    id: int

    imdb_nmid: str
    name_en: str
    slug: str

    birth_y: int | None
    death_y: int | None
    image_url: str | None

    tmdb_added: bool
    imdb_extra_added: bool

    ## Relations

    ## not in use
    # tmdb: "TMDbPersonDTO" | None = None
    # professions: list["PersonProfessionsDTO"] = []
    # movies: list["MoviePrincipalsDTO"] = []


class ProfessionDTO(BaseModel):
    id: int
    imdb_name: str
    name_en: str
    name_ru: str

    ## Relations

    ## not in use
    # persons_by_profession: list["PersonProfessionsDTO"] = []
    # movies_by_profession: list["MoviePrincipalsDTO"] = []


class PersonProfessionsDTO(BaseModel):
    id: int

    ## Relations
    profession: ProfessionDTO

    ## not in use
    # person: IMDbPersonDTOBase


class MoviePrincipalDTO(BaseModel):
    id: int

    ordering: int
    job: str | None = None
    characters: list[str] = []

    ## Relations

    ## not in use
    # imdb_movie: IMDbMovieBaseDTO
    # imdb_person: IMDbPersonDTOBase
    # professioN: ProfessionDTO


class MoviePrincipalMovieDTO(MoviePrincipalDTO):
    imdb_movie: IMDbMovieBaseDTO


class MoviePrincipalPersonDTO(MoviePrincipalDTO):
    imdb_person: IMDbPersonDTOBase


class TMDbPersonDTO(BaseModel):
    id: int
    tmdb_nmid: int

    name_en: str
    name_ru: str | None

    gender: int

    ## Relations

    ## not in use
    # imdb: IMDbMovieBaseDTO


class IMDbPersonDTOExtended(IMDbPersonDTOBase):
    tmdb: Optional["TMDbPersonDTO"]
    professions: list["PersonProfessionsDTO"] = []
    movies: list["MoviePrincipalMovieDTO"] = []
