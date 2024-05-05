import asyncio

from add_genres import GenresAdder, genres
from add_countries import CountriesAdder, countries
from add_movie_types import MovieTypesAdder, types

from add_imdb_movie import IMDbMovieAdder, IMDbDataSet, settings, IMDbMovie
from add_tmdb_movie import TMDbMovieAdder
from add_imdb_extra import IMDbExtraAdder


async def main():
    await GenresAdder().add_all(genres)
    await CountriesAdder().add_all(countries)
    await MovieTypesAdder().add_all(types)

    dataset = IMDbDataSet()
    imdb_movies: list[IMDbMovie] = dataset.get_movies(10000, settings.DEBUG)
    await IMDbMovieAdder().add_all(imdb_movies)
    await TMDbMovieAdder().add_all()

    ## Problem with blocking (cooldown) on IMDb side
    ## Need to investigate cooldown time and limits req per sec
    # await IMDbExtraAdder().add_all()


if __name__ == "__main__":
    asyncio.run(main())
