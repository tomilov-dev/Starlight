import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))


from database.manager import DatabaseManager
from movies.orm import CountryORM
from services.countries import countries


class CountryManager(DatabaseManager):
    ORM = CountryORM


async def countries_init():
    manager = CountryManager()
    await manager.goc_batch(countries)


if __name__ == "__main__":
    asyncio.run(countries_init())
