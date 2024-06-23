import sys
from pathlib import Path
from fastapi import APIRouter


sys.path.append(Path(__file__).parent.parent)

from movies.manager.imdb_movie import IMDbMovieManager
from movies.manager.genre import GenreManager
from movies.models import IMDbDTO, GenreDTO, GenreMoviesDTO

imdbM = IMDbMovieManager()
genresM = GenreManager()

router = APIRouter()


@router.get("/movies/{slug}")
async def get_movie(slug: str):
    movie = await imdbM.getj(slug=slug)
    if isinstance(movie, list):
        movie = movie[0]

    movie = IMDbDTO.model_validate(movie, from_attributes=True)
    return movie


@router.get("/genres")
async def get_genres():
    genres = await genresM.get()
    genres = [GenreDTO.model_validate(g, from_attributes=True) for g in genres]
    return genres


@router.get("/genres/{slug}")
async def get_genre(slug: str):
    genre, movies = await genresM.get_genre(slug)

    genre = GenreMoviesDTO(
        id=genre.id,
        name_en=genre.name_en,
        name_ru=genre.name_ru,
        slug=genre.slug,
        movies=[IMDbDTO.model_validate(m, from_attributes=True) for m in movies],
    )

    return genre, movies
