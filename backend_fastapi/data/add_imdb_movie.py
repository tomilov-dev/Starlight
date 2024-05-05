import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import IMDbORM, MovieTypeORM, GenreORM, MovieGenreORM
from backend_fastapi.settings import settings
from services.imdb.dataset import IMDbMovie, IMDbDataSet


class IMDbMovieAdder(DatabaseAdder):
    async def add_imdb_genres(self, imdb_data: IMDbMovie) -> None:
        movie = await self.mvdb.get(IMDbORM, imdb_mvid=imdb_data.imdb_mvid)
        if movie:
            movie: IMDbORM = movie[0]

            genres = [self.genres[g] for g in imdb_data.genres]
            movie_genres = [
                MovieGenreORM(imdb_movie=movie.id, genre=g.id) for g in genres
            ]

            tasks = [self.mvdb.insert_movie_genre(mg) for mg in movie_genres]
            await asyncio.gather(*tasks)

    async def create_imdb(self, imdb_data: IMDbMovie) -> IMDbORM:
        movie_type: MovieTypeORM = self.types[imdb_data.type]
        slug = await self.mvdb.create_slug(imdb_data.init_slug, IMDbORM)

        imdb = IMDbORM(
            imdb_mvid=imdb_data.imdb_mvid,
            movie_type=movie_type.id,
            title_en=imdb_data.title_en,
            title_ru=imdb_data.title_ru,
            slug=slug,
            is_adult=imdb_data.is_adult,
            runtime=imdb_data.runtime,
            rate=imdb_data.rate,
            wrate=imdb_data.wrate,
            votes=imdb_data.votes,
        )

        await self.mvdb.insert_imdb(imdb)

    async def add_all(
        self,
        imdb_movies: list[IMDbMovie],
    ) -> None:
        movie_types: list[MovieTypeORM] = await self.mvdb.get(MovieTypeORM)
        self.types = {mt.name_en.lower(): mt for mt in movie_types}

        genres: list[GenreORM] = await self.mvdb.get(GenreORM)
        self.genres = {g.imdb_name: g for g in genres}

        current_imdbs = await self.mvdb.get(IMDbORM, IMDbORM.imdb_mvid, IMDbORM.slug)
        created_imdbs = {ci.imdb_mvid for ci in current_imdbs}
        created_slugs = {ci.slug for ci in current_imdbs}

        imdb_movies = [m for m in imdb_movies if m.imdb_mvid not in created_imdbs]
        for m in imdb_movies:
            m.set_init_slug(self.mvdb.initiate_slug(m.title_en, created_slugs))

        tasks = [self.create_imdb(md) for md in imdb_movies]
        await asyncio.gather(*tasks)

        tasks = [self.add_imdb_genres(md) for md in imdb_movies]
        await asyncio.gather(*tasks)


async def main():
    dataset = IMDbDataSet()
    imdb_movies: list[IMDbMovie] = dataset.get_movies(10000, settings.DEBUG)

    adder = IMDbMovieAdder()
    await adder.add_all(imdb_movies)


if __name__ == "__main__":
    asyncio.run(main())
