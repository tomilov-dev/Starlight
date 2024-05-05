import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import GenreORM
from services.movie_genres import genres, GenreObj


class GenresAdder(DatabaseAdder):
    async def add_all(
        self,
        genres: list[GenreObj],
    ) -> None:
        genres = [
            GenreORM(
                imdb_name=g.imdb,
                slug=g.slug,
                tmdb_name=g.tmdb,
                name_ru=g.name_ru,
            )
            for g in genres
        ]

        await self.mvdb.insertb_genres(genres)


async def main():
    adder = GenresAdder()
    await adder.add_all(genres)


if __name__ == "__main__":
    asyncio.run(main())
