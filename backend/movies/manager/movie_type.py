import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.manager import DatabaseManager
from movies.orm import MovieTypeORM
from services.movie_types import movie_types


class MovieTypeManager(DatabaseManager):
    ORM = MovieTypeORM


async def movie_types_init():
    manager = MovieTypeManager()
    await manager.goc_batch(movie_types)


if __name__ == "__main__":
    asyncio.run(movie_types_init())
