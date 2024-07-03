import sys
import asyncio
from abc import ABC, abstractmethod
from typing import Type
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from database.api import DataBaseAPI
from services.countries import CountrySDM
from movies.orm import CountryORM


class TestCase:
    name_en = "test_country"
    name_ru = "тестовая_страна"
    new_name_en = "new_name_en"
    iso = "XZ"


class APISingleTest(ABC):
    def __init__(
        self,
        api: DataBaseAPI,
        tc: Type[TestCase],
    ) -> None:
        self.api = api
        self.tc = tc

    def get_instance(self) -> CountrySDM:
        return CountrySDM(
            name_en=self.tc.name_en,
            name_ru=self.tc.name_ru,
            iso=self.tc.iso,
        )

    @abstractmethod
    async def add(self):
        pass

    @abstractmethod
    async def get_full(self):
        pass

    @abstractmethod
    async def get_part(self):
        pass

    @abstractmethod
    async def exists(self):
        pass

    @abstractmethod
    async def goc(self):
        pass

    @abstractmethod
    async def delete(self):
        pass

    @abstractmethod
    async def update(self):
        pass

    @abstractmethod
    async def upsert_insert(self):
        pass

    @abstractmethod
    async def upsert_update(self):
        pass

    async def test(self):
        country = self.get_instance()

        async with self.api.session as session:
            print("Add")
            await self.add(session, country)

            print("Get full")
            await self.get_full(session, country)
            print("Get part")
            await self.get_part(session, country)
            print("Check existence")
            await self.exists(session, country, True)

            print("GoC: Get")
            await self.goc(session, country)
            print("Delete 1")
            await self.delete(session, country)
            print("GoC: Create")
            await self.goc(session, country)

            print("Update")
            await self.update(session, country)
            print("Delete 2")
            await self.delete(session, country)

            print("Upsert: Insert")
            await self.upsert_insert(session, country)
            print("Upsert: Update")
            await self.upsert_update(session, country)
            print("Delete 3")
            await self.delete(session, country)


class BasicAPITest(APISingleTest):
    async def add(self, session: AsyncSession, country: CountrySDM) -> None:
        await self.api.add(
            CountryORM,
            session,
            name_en=country.name_en,
            name_ru=country.name_ru,
            iso=country.iso,
        )

    async def get_full(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.get(CountryORM, session, iso=country.iso)
        assert country.name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def get_part(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.get(CountryORM, session, CountryORM.iso, iso=country.iso)
        assert country.iso == data.iso
        assert not hasattr(data, "name_en")
        assert not hasattr(data, "name_ru")

    async def exists(
        self,
        session: AsyncSession,
        country: CountrySDM,
        exist_status: bool,
    ) -> None:
        exists = await self.api.exists(CountryORM, session, iso=country.iso)
        assert exists == exist_status

    async def delete(self, session: AsyncSession, country: CountrySDM) -> None:
        await self.api.delete(CountryORM, session, iso=country.iso)
        await self.exists(session, country, False)

    async def goc(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.goc(
            CountryORM,
            session,
            name_en=country.name_en,
            name_ru=country.name_ru,
            iso=country.iso,
        )
        assert country.name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def update(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.update(
            CountryORM,
            session,
            filters={"iso": country.iso},
            name_en=self.tc.new_name_en,
        )

        assert self.tc.new_name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def upsert_insert(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.upsert(
            CountryORM,
            session,
            name_en=country.name_en,
            name_ru=country.name_ru,
            iso=country.iso,
        )
        assert country.name_en == data.name_ne
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def upsert_update(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.upsert(
            CountryORM,
            session,
            name_en=self.tc.new_name_en,
            name_ru=country.name_ru,
            iso=country.iso,
        )
        assert self.tc.new_name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso


class RecordAPITest(APISingleTest):
    async def add(self, session: AsyncSession, country: CountrySDM) -> None:
        orm = CountryORM.from_pydantic(country)
        await self.api.radd(orm, session)

    async def get_full(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.get(CountryORM, session, iso=country.iso)
        assert country.name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def get_part(self, session: AsyncSession, country: CountrySDM) -> None:
        data = await self.api.get(CountryORM, session, CountryORM.iso, iso=country.iso)
        assert country.iso == data.iso
        assert not hasattr(data, "name_en")
        assert not hasattr(data, "name_ru")

    async def exists(
        self,
        session: AsyncSession,
        country: CountrySDM,
        exists_status: bool,
    ) -> None:
        orm = CountryORM.from_pydantic(country)
        exists = await self.api.rexists(orm, session)
        assert exists == exists_status

    async def delete(self, session: AsyncSession, country: CountrySDM) -> None:
        orm = CountryORM.from_pydantic(country)
        await self.api.rdelete(orm, session)
        await self.exists(session, country, False)

    async def goc(self, session: AsyncSession, country: CountrySDM) -> None:
        orm = CountryORM.from_pydantic(country)
        data = await self.api.rgoc(orm, session)
        assert country.name_en == data.name_en
        assert country.name_ru == data.name_ru
        assert country.iso == data.iso

    async def update(self, session: AsyncSession, country: CountrySDM) -> None:
        raise NotImplementedError()

    async def upsert_insert(self, session: AsyncSession, country: CountrySDM) -> None:
        raise NotImplementedError()

    async def upsert_update(self, session: AsyncSession, country: CountrySDM) -> None:
        raise NotImplementedError()


async def hand_test():
    # test = BasicAPITest(DataBaseAPI(), TestCase)
    test = RecordAPITest(DataBaseAPI(), TestCase)

    await test.test()


if __name__ == "__main__":
    asyncio.run(hand_test())
