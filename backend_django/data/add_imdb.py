import os
import sys
import asyncio
import django
from pathlib import Path
from slugify import slugify
from tqdm.asyncio import tqdm_asyncio
from django.apps import apps
from django.db.utils import IntegrityError
from django.db.models import Model

PROJ_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJ_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "starlight_backend.settings")
django.setup()


from services.imdb.dataset import IMDbDataSet, IMDbMovie
from movies.models import IMDb, MovieGenre, Genre


class IMDbAdder(object):
    def __init__(self, dataset: IMDbDataSet) -> None:
        self._dataset = dataset

    def slugify(
        self,
        text: str,
        extra: str | None = None,
    ) -> str:
        slug = slugify(
            text,
            separator="-",
            replacements=[["_", "-"]],
        )
        if extra is not None:
            slug += "-" + extra

        return slug

    async def slug_exists(self, slug: str, model: Model) -> bool:
        try:
            exists = False
            await model.objects.aget(slug=slug)
            exists = True
        except Model.DoesNotExist:
            exists = False
        finally:
            return exists

    async def get_slug(
        self,
        text: str,
        extra: str,
        model: Model,
    ) -> str:
        slug = self.slugify(text)
        if await self.slug_exists(slug, model):
            slug = self.slugify(text, extra)

        return slug

    async def create_movie(self, movie: IMDbMovie) -> IMDb | None:
        movie_obj = None

        try:
            slug = await self.get_slug(
                movie.title_en,
                movie.imdb_mvid,
                IMDb,
            )

            movie_obj = await IMDb.objects.acreate(
                imdb_mvid=movie.imdb_mvid,
                type=movie.type,
                title_en=movie.title_en,
                title_ru=movie.title_ru,
                slug=slug,
                is_adult=movie.is_adult,
                runtime=movie.runtime,
                rate=movie.rate,
                wrate=movie.wrate,
                votes=movie.votes,
            )

        except IntegrityError:
            movie_obj = None

        finally:
            return movie_obj

    async def get_genre(self, imdb_genre_name: str) -> Genre:
        slug = await self.get_slug(imdb_genre_name, "genre", Genre)

        genre_obj = await Genre.objects.aget_or_create(
            imdb_name=imdb_genre_name,
            defaults={"slug": slug},
        )

        return genre_obj

    async def create_movie_genre(self, imdb: IMDb, genre: Genre) -> MovieGenre | None:
        movie_genre = None

        try:
            movie_genre = await MovieGenre.objects.acreate(
                imdb_mvid=imdb,
                genre=genre,
            )

        except IntegrityError:
            movie_genre = None

        finally:
            return movie_genre

    async def add(self, movie: IMDbMovie) -> None:
        movie_obj = await self.create_movie(movie)
        if movie_obj is not None:
            if movie.genres:
                tasks = [
                    asyncio.create_task(self.get_genre(genre_name))
                    for genre_name in movie.genres
                ]

                genres_objs = await asyncio.gather(*tasks)

                tasks = [
                    asyncio.create_task(self.create_movie_genre(movie_obj, genre_obj))
                    for genre_obj in genres_objs
                ]

                await asyncio.gather(*tasks)

    async def add_all(self) -> None:
        # scraper is not asynchrone
        print("Download IMDb data")
        movies = self._dataset.get_movies(1000)

        print("Add IMDb data")
        tasks = [asyncio.create_task(self.add(movie)) for movie in movies]
        await tqdm_asyncio.gather(*tasks, total=len(tasks))

        # await asyncio.gather(*tasks)


async def main():
    dataset = IMDbDataSet()
    adder = IMDbAdder(dataset)

    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
