from pydantic import BaseModel


class MovieTypeDTO(BaseModel):
    id: int
    name_en: str
    name_ru: str

    ## Relations
    ## not in use
    # imdb_movies: list["IMDbMovieBaseDTO"] = []


class IMDbMovieBaseDTO(BaseModel):
    id: int
    imdb_mvid: str

    name_en: str
    name_ru: str | None = None
    slug: str

    is_adult: bool
    runtime: int | None = None

    rate: float | None = None
    wrate: float | None = None
    votes: int | None = None

    start_year: int
    end_year: int | None = None
    image_url: str | None = None

    imdb_extra_added: bool
    tmdb_added: bool
    principals_added: bool

    ## Relations
    type: MovieTypeDTO

    ## Other relations determined in extended model
