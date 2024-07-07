import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query


sys.path.append(Path(__file__).parent.parent)

from movies.manager.imdb_movie import IMDbMovieManager, MoviesOrderBy
from movies.manager.genre import GenreManager
from movies.manager.country import CountryManager
from movies.models import (
    GenreDTO,
    CountryDTO,
    IMDbMovieBaseDTO,
    IMDbMovieExtendedDTO,
    ProductionCompanyDTO,
)

imdbM = IMDbMovieManager()
genresM = GenreManager()
countriesM = CountryManager()

router = APIRouter()


@router.get("/genres")
async def get_genres() -> list[GenreDTO]:
    genres = await genresM.get_genres()
    return [GenreDTO.model_validate(g, from_attributes=True) for g in genres]


@router.get("/countries")
async def get_countries() -> list[CountryDTO]:
    countries = await countriesM.get_countries()
    return [CountryDTO.model_validate(c, from_attributes=True) for c in countries]


@router.get("/search/movies/{query}")
async def search_movies(query: str) -> list[IMDbMovieBaseDTO]:
    movies = await imdbM.search_movies(query)
    return [IMDbMovieBaseDTO.model_validate(m, from_attributes=True) for m in movies]


@router.get("/select/movies")
async def select_movies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10, le=100),
    include_genre: list[int] | None = Query(None),
    exclude_genre: list[int] | None = Query(None),
    include_country: list[int] | None = Query(None),
    exclude_country: list[int] | None = Query(None),
    order_by: MoviesOrderBy = MoviesOrderBy.DEFAULT,
    asc: bool = Query(False),
    start_year: int = Query(None, ge=1900, le=2050),
    end_year: int = Query(None, ge=1900, le=2050),
    rate: float = Query(None, ge=0, le=10),
    votes: int = Query(None, ge=0),
    wrate: float = Query(None, ge=0, le=10),
    adult: bool = Query(None),
) -> list[IMDbMovieBaseDTO]:
    movies = await imdbM.select_movies(
        page=page,
        page_size=page_size,
        include_genre=include_genre,
        exclude_genre=exclude_genre,
        include_country=include_country,
        exclude_country=exclude_country,
        order_by=order_by,
        ascending=asc,
        start_year=start_year,
        end_year=end_year,
        rate=rate,
        votes=votes,
        wrate=wrate,
        adult=adult,
    )

    if not movies:
        raise HTTPException(
            status_code=404,
            detail="Movies not found",
        )

    return [IMDbMovieBaseDTO.model_validate(m, from_attributes=True) for m in movies]


@router.get("/movies/{slug}")
async def get_movie(slug: str) -> IMDbMovieExtendedDTO:
    movie = await imdbM.get_extended_movie_data(slug=slug)
    if not movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    return IMDbMovieExtendedDTO.model_validate(movie, from_attributes=True)


@router.get("/genres/{slug}")
async def get_movies_by_genre(
    slug: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10, le=100),
    order_by: MoviesOrderBy = MoviesOrderBy.DEFAULT,
    asc: bool = Query(False),
    start_year: int = Query(None, ge=1900, le=2050),
    end_year: int = Query(None, ge=1900, le=2050),
    rate: float = Query(None, ge=0, le=10),
    votes: int = Query(None, ge=0),
    wrate: float = Query(None, ge=0, le=10),
    adult: bool = Query(None),
) -> list[IMDbMovieBaseDTO]:
    movies = await imdbM.get_movies_by_genre(
        genre_slug=slug,
        page=page,
        page_size=page_size,
        order_by=order_by,
        ascending=asc,
        start_year=start_year,
        end_year=end_year,
        rate=rate,
        votes=votes,
        wrate=wrate,
        adult=adult,
    )

    if not movies:
        raise HTTPException(
            status_code=404,
            detail="Movies not found",
        )

    return [IMDbMovieBaseDTO.model_validate(m, from_attributes=True) for m in movies]
