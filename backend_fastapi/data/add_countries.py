import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from movies.orm import CountryORM
from services.countries import countries, CountryObj


class CountriesAdder(DatabaseAdder):
    async def add_all(
        self,
        countries: list[CountryObj],
    ) -> None:
        countries = [
            CountryORM(
                iso=c.iso,
                name_en=c.name_en,
                name_ru=c.name_ru,
            )
            for c in countries
        ]

        await self.mvdb.insertb_countries(countries)


async def main():
    adder = CountriesAdder()
    await adder.add_all(countries)


if __name__ == "__main__":
    asyncio.run(main())
