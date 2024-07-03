import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

# from database.manager import DatabaseManager
from database.api import DataBaseAPI
from movies.orm import CountryORM
from services.countries import countries


# class CountryManager(DatabaseManager):
#     ORM = CountryORM


async def countries_init():
    # manager = CountryManager()
    # await manager.goc_batch(countries)

    country = countries[0]
    print(country)

    api = DataBaseAPI()
    async with api.session as session:
        record = await api.goc(
            CountryORM,
            session,
            name_en=country.name_en,
            name_ru=country.name_ru,
            iso=country.iso,
        )
        print(record.id)


if __name__ == "__main__":
    asyncio.run(countries_init())
