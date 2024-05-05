import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import MovieTypeORM
from services.movie_types import types, TypeObj


class MovieTypesAdder(DatabaseAdder):
    async def add_all(
        self,
        types: list[TypeObj],
    ) -> None:
        types = [
            MovieTypeORM(
                name_en=t.name_en,
                name_ru=t.name_ru,
            )
            for t in types
        ]

        print("Batch Insert Movie Types")
        async with self.mvdb.session as session:
            await self.mvdb.insertb(types, session)
            await session.commit()


async def main():
    adder = MovieTypesAdder()
    await adder.add_all(types)


if __name__ == "__main__":
    asyncio.run(main())
