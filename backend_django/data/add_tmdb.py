import os
import sys
import asyncio
import traceback
import django
from pathlib import Path
from typing import Callable, Any
from functools import wraps
from tqdm.asyncio import tqdm_asyncio
from asgiref.sync import sync_to_async
from django.db.models import Model

PROJ_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJ_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starlight_backend.settings")
django.setup()

PROXY = "138.59.5.129:9827@66M48j:6oxuwq"

from movies.models import (
    IMDb,
    TMDb,
    Country,
    MovieCountry,
    ProductionCompany,
    MovieProduction,
    Genre,
    MovieGenre,
    Collection,
)
from services.tmdb.scraper import TMDbScraper, MovieDoesNotExist, TMDbMovie, Production


class TMDbAdderCrush(Exception):
    pass


def expect(func: Callable) -> Callable:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)

        except Exception as ex:
            print(f"Error in '{func.__name__}': {ex}")
            print(traceback.format_exc())
            raise TMDbAdderCrush

    return wrapper


class TMDbAdder(object):
    def __init__(
        self,
        scraper: TMDbScraper,
    ) -> None:
        self._scraper = scraper
        self._loop = None

    async def setup_loop(self) -> None:
        self._loop = asyncio.get_running_loop()

    async def get_movie(self, imdb_mvid: str) -> TMDbMovie | None:
        movie = None
        try:
            movie = await self._scraper.get_movie(imdb_mvid)

        except MovieDoesNotExist:
            movie = None

        finally:
            return movie

    async def create_collection(
        self,
        movie: TMDbMovie,
    ) -> Collection | None:
        collection = None
        if movie.collection:
            collection, _ = await Collection.objects.aget_or_create(
                id=movie.collection.id,
                defaults={"name_en": movie.collection.name},
            )
        return collection

    @expect
    async def create_tmdb(
        self,
        imdb: IMDb,
        movie: TMDbMovie,
    ) -> TMDb:
        collection = await self.create_collection(movie)

        tmdb, _ = await TMDb.objects.aget_or_create(
            imdb_mvid=imdb,
            tmdb_mvid=movie.tmdb_mvid,
            collection=collection,
            release_date=movie.release_date,
            budget=movie.budget,
            revenue=movie.revenue,
            image_url=movie.image_url,
            tagline_en=movie.tagline_en,
            overview_en=movie.overview_en,
            tagline_ru=movie.tagline_ru,
            overview_ru=movie.overview_ru,
            rate=movie.rate,
            votes=movie.votes,
            popularity=movie.popularity,
        )

        return tmdb

    async def get_country(self, country_name: str) -> Country:
        country, _ = await Country.objects.aget_or_create(
            name=country_name,
        )
        return country

    async def create_movie_country(
        self,
        country: str,
        imdb: IMDb,
        tmdb: TMDb,
    ) -> MovieCountry:
        movie_country = await MovieCountry.objects.acreate(
            country=country,
            imdb_mvid=imdb,
            tmdb_mvid=tmdb,
        )
        return movie_country

    @expect
    async def add_countries(
        self,
        imdb: IMDb,
        tmdb: TMDb,
        movie: TMDbMovie,
    ) -> None:
        if movie.countries:
            tasks = [
                asyncio.create_task(
                    self.get_country(country_name),
                )
                for country_name in movie.countries
            ]
            countries = await asyncio.gather(*tasks)

            tasks = [
                asyncio.create_task(
                    self.create_movie_country(
                        country,
                        imdb,
                        tmdb,
                    )
                )
                for country in countries
            ]

            await asyncio.gather(*tasks)

    async def get_production(
        self,
        production: Production,
    ) -> ProductionCompany:
        production, _ = await ProductionCompany.objects.aget_or_create(
            company=production.id,
            defaults={
                "name": production.name,
                "country": production.country,
                "image_url": production.image_url,
            },
        )
        return production

    async def create_movie_production(
        self,
        production: ProductionCompany,
        imdb: IMDb,
        tmdb: TMDb,
    ) -> MovieProduction:
        movie_prod = await MovieProduction.objects.acreate(
            company=production,
            imdb_mvid=imdb,
            tmdb_mvid=tmdb,
        )
        return movie_prod

    @expect
    async def add_productions(
        self,
        imdb: IMDb,
        tmdb: TMDb,
        movie: TMDbMovie,
    ) -> None:
        productions = movie.productions
        if productions:
            tasks = [
                asyncio.create_task(self.get_production(production))
                for production in productions
            ]

            productions = await asyncio.gather(*tasks)

            tasks = [
                asyncio.create_task(
                    self.create_movie_production(
                        production,
                        imdb,
                        tmdb,
                    )
                )
                for production in productions
            ]

            await asyncio.gather(*tasks)

    async def get_genre(self, genre_name: str) -> Genre | None:
        genre = None
        try:
            genre = await Genre.objects.aget(
                tmdb_name=genre_name,
            )

        except Model.DoesNotExist:
            genre = None

        finally:
            return genre

    async def create_movie_genre(
        self,
        imdb: IMDb,
        genre: Genre | None,
    ) -> MovieGenre | None:
        movie_genre = None
        if genre:
            movie_genre = await MovieGenre.objects.acreate(
                imdb_mvid=imdb,
                genre=genre,
            )

        return movie_genre

    @expect
    async def add_genres(
        self,
        imdb: IMDb,
        tmdb: TMDb,
        movie: TMDbMovie,
    ) -> None:
        genres_names = movie.genres
        if genres_names:
            tasks = [
                asyncio.create_task(self.get_genre(genre_name))
                for genre_name in genres_names
            ]
            genres = await asyncio.gather(*tasks)

            tasks = [
                asyncio.create_task(self.create_movie_genre(imdb, genre))
                for genre in genres
            ]

            await asyncio.gather(*tasks)

    @expect
    async def add_ru_title(
        self,
        imdb: IMDb,
        tmdb: TMDb,
        movie: TMDbMovie,
    ) -> None:
        if movie.title_ru:
            if not imdb.title_ru:
                imdb.title_ru = movie.title_ru
                await imdb.asave()

    async def mark_up(self, imdb: IMDb) -> None:
        imdb.tmdb_added = True
        await imdb.asave()

    async def add(self, imdb: IMDb) -> None:
        imdb_mvid = imdb.imdb_mvid
        try:

            movie = await self.get_movie(imdb_mvid)
            # movie.show_data()

            if movie:
                tmdb = await self.create_tmdb(imdb, movie)

                tasks = [
                    self._loop.create_task(self.add_countries(imdb, tmdb, movie)),
                    self._loop.create_task(self.add_productions(imdb, tmdb, movie)),
                    self._loop.create_task(self.add_genres(imdb, tmdb, movie)),
                    self._loop.create_task(self.add_ru_title(imdb, tmdb, movie)),
                ]
                await asyncio.gather(*tasks)

            await self.mark_up(imdb)

        except TMDbAdderCrush:
            print("Crushed at IMDb ID:", imdb_mvid)

    async def add_with_imdb_mvid(self, imdb_mvid) -> None:
        """Only for test purposes"""
        if not self._loop:
            await self.setup_loop()

        imdb = await IMDb.objects.aget(imdb_mvid=imdb_mvid)
        await self.add(imdb)

    async def add_all(self) -> None:
        if not self._loop:
            await self.setup_loop()

        print("Collect movies without tmdb_added mark")
        movies = IMDb.objects.filter(tmdb_added=False)

        print("Add TMDb data")
        tasks = [self._loop.create_task(self.add(movie)) async for movie in movies]
        await tqdm_asyncio.gather(*tasks, total=len(tasks))


async def main():
    proxy = PROXY
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZWIzNGQxNGJhZWEwM2JiZjRmYTVhZTkzNTdjYTllZSIsInN1YiI6IjY1YWQzODIyMjVjZDg1MDBlYTBjYjgzMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.o7Q5t7MZiKC3SnXs2vYmdGSY6HWMg4PZdYcSMANKOSc"

    scraper = TMDbScraper(api_key, proxy, 45, 1)
    adder = TMDbAdder(scraper)

    await adder.add_all()


async def test():
    proxy = PROXY
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZWIzNGQxNGJhZWEwM2JiZjRmYTVhZTkzNTdjYTllZSIsInN1YiI6IjY1YWQzODIyMjVjZDg1MDBlYTBjYjgzMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.o7Q5t7MZiKC3SnXs2vYmdGSY6HWMg4PZdYcSMANKOSc"

    scraper = TMDbScraper(api_key, proxy, 45, 1)
    tmdb = TMDbAdder(scraper)

    movie = await scraper.get_movie("tt0499549")
    await tmdb.add_with_imdb_mvid(movie.imdb_mvid)


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(test())
