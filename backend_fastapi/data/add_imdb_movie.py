import sys
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import IMDbORM, MovieTypeORM, GenreORM, MovieGenreORM
from backend_fastapi.settings import settings
from services.imdb.dataset import IMDbMovie, IMDbDataSet


class IMDbMovieAdder(DatabaseAdder):
    async def add_imdb_genres(
        self,
        imdb_data: IMDbMovie,
        imdb_id: int,
    ) -> None:
        async with self.mvdb.session as session:
            genres = [self.genres[g] for g in imdb_data.genres]
            movie_genres = [
                MovieGenreORM(
                    imdb_movie=imdb_id,
                    genre=g.id,
                )
                for g in genres
            ]

            tasks = [self.mvdb.insert(mg, session) for mg in movie_genres]
            await asyncio.gather(*tasks)
            await session.commit()

    def setup_imdb(
        self,
        imdb_data: IMDbMovie,
        movie_type: MovieTypeORM,
        slug: str,
    ) -> IMDbORM:
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
        return imdb

    async def create_imdb(self, imdb_data: IMDbMovie) -> int:
        async with self.mvdb.session as session:
            movie_type: MovieTypeORM = self.types[imdb_data.type]
            slug = await self.mvdb.create_slug(imdb_data.init_slug, IMDbORM, session)
            imdb = self.setup_imdb(imdb_data, movie_type, slug)

            await self.mvdb.insert(imdb, session)
            await session.commit()
            await session.refresh(imdb)

            return imdb.id

    async def add_all(
        self,
        imdb_movies: list[IMDbMovie],
    ) -> None:
        async with self.mvdb.session as session:
            movie_types: list[MovieTypeORM] = await self.mvdb.get(MovieTypeORM, session)
            self.types = {mt.name_en.lower(): mt for mt in movie_types}

            genres: list[GenreORM] = await self.mvdb.get(GenreORM, session)
            self.genres = {g.imdb_name: g for g in genres}

            current_imdbs = await self.mvdb.get(
                IMDbORM,
                session,
                IMDbORM.imdb_mvid,
                IMDbORM.slug,
            )
            created_imdbs = {ci.imdb_mvid for ci in current_imdbs}
            created_slugs = {ci.slug for ci in current_imdbs}

        imdb_movies = [m for m in imdb_movies if m.imdb_mvid not in created_imdbs]
        for m in imdb_movies:
            m.set_init_slug(self.mvdb.initiate_slug(m.title_en, created_slugs))

        tasks = [self.create_imdb(md) for md in imdb_movies]

        print("Insert IMDb Movies")
        imdb_ids = await tqdm_asyncio.gather(*tasks)

        if len(imdb_movies) != len(imdb_ids):
            raise ValueError("Count of IMDb records doesn't equal to uploaded ids")

        tasks = [
            self.add_imdb_genres(imdb_movies[i], imdb_ids[i])
            for i in range(len(imdb_movies))
        ]

        print("Insert IMDb Movie Genres")
        await tqdm_asyncio.gather(*tasks)


async def main():
    dataset = IMDbDataSet()
    imdb_movies: list[IMDbMovie] = dataset.get_movies(10000, settings.DEBUG)

    adder = IMDbMovieAdder()
    await adder.add_all(imdb_movies)


if __name__ == "__main__":
    asyncio.run(main())
