import sys
import asyncio
from abc import ABC, abstractmethod
import pytest
from typing import Type
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from database.core import TRelationORM
from database.api import DataBaseAPI


class TCase:
    def __init__(
        self,
        attr1: int,
        attr2: int,
        attr3: int,
        new_attr1: int,
        attr4: int | None = None,
    ):
        self.attr1 = attr1
        self.attr2 = attr2
        self.attr3 = attr3
        self.attr4 = attr4

        self.new_attr1 = new_attr1

    @property
    def attrs(self) -> dict[str, int]:
        return {
            "attr1": self.attr1,
            "attr2": self.attr2,
            "attr3": self.attr3,
        }

    @property
    def all_attrs(self) -> dict[str, int]:
        return {
            "attr1": self.attr1,
            "attr2": self.attr2,
            "attr3": self.attr3,
            "attr4": self.attr4,
        }


TEST_CASES = [
    TCase(1, 5, 9, 2),
    TCase(10, 50, 90, 20),
    TCase(100, 500, 900, 200),
    TCase(1000, 5000, 9000, 2000),
    TCase(10000, 50000, 90000, 20000),
]


class APISingleBaseTest(ABC):
    def __init__(
        self,
        api: DataBaseAPI,
        tc: TCase,
    ) -> None:
        self.api = api
        self.tc = tc

    @abstractmethod
    async def add(self):
        pass

    @abstractmethod
    async def add_safe(self):
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
    async def delete_new(self):
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
        async with self.api.session as session:
            print("Add")
            id = await self.add(session)
            assert isinstance(id, int)

            print("Add Safe")
            await self.add_safe(session)

            print("Get full")
            await self.get_full(session)
            print("Get part")
            await self.get_part(session)
            print("Check existence")
            await self.exists(session, True)

            print("GoC: Get")
            await self.goc(session)
            print("Delete 1")
            await self.delete(session)
            print("GoC: Create")
            await self.goc(session)

            print("Update")
            await self.update(session)
            print("Delete 2")
            await self.delete_new(session)


class APIBulkBaseTest(ABC):
    def __init__(
        self,
        api: DataBaseAPI,
        tcs: TCase,
    ) -> None:
        self.api = api
        self.tcs = tcs

    @abstractmethod
    async def badd(self, session: AsyncSession):
        pass

    @abstractmethod
    async def badd_safe(self, session: AsyncSession):
        pass

    @abstractmethod
    async def bget_full(self, session: AsyncSession):
        pass

    @abstractmethod
    async def bget_part(self, session: AsyncSession):
        pass

    @abstractmethod
    async def delete(self, session: AsyncSession):
        pass

    async def test(self):
        async with self.api.session as session:
            await self.badd(session)
            await self.badd_safe(session)

            await self.bget_full(session)
            await self.bget_part(session)

            await self.delete(session)


class BasicAPITest(APISingleBaseTest):
    async def add(self, session: AsyncSession) -> None:
        return await self.api.add(
            TRelationORM,
            session,
            **self.tc.attrs,
        )

    async def add_safe(self, session: AsyncSession) -> None:
        return await self.api.add(
            TRelationORM,
            session,
            _safe_add=True,
            **self.tc.attrs,
        )

    async def get_full(self, session: AsyncSession) -> None:
        data = await self.api.get(TRelationORM, session, attr1=self.tc.attr1)
        assert self.tc.attr1 == data.attr1
        assert self.tc.attr2 == data.attr2
        assert self.tc.attr3 == data.attr3

    async def get_part(self, session: AsyncSession) -> None:
        data = await self.api.get(
            TRelationORM,
            session,
            TRelationORM.attr1,
            attr1=self.tc.attr1,
        )
        assert self.tc.attr1 == data.attr1
        assert not hasattr(data, "attr2")
        assert not hasattr(data, "attr3")

    async def exists(
        self,
        session: AsyncSession,
        exist_status: bool,
    ) -> None:
        exists = await self.api.exists(TRelationORM, session, attr1=self.tc.attr1)
        assert exists == exist_status

    async def delete(self, session: AsyncSession) -> None:
        await self.api.delete(TRelationORM, session, attr1=self.tc.attr1)
        await self.exists(session, False)

    async def delete_new(self, session: AsyncSession) -> None:
        await self.api.delete(TRelationORM, session, attr1=self.tc.new_attr1)
        await self.exists(session, False)

    async def goc(self, session: AsyncSession) -> None:
        data = await self.api.goc(TRelationORM, session, **self.tc.attrs)
        assert self.tc.attr1 == data.attr1
        assert self.tc.attr2 == data.attr2
        assert self.tc.attr3 == data.attr3

    async def update(self, session: AsyncSession) -> None:
        data = await self.api.update(
            TRelationORM,
            session,
            filters={"attr1": self.tc.attr1},
            attr1=self.tc.new_attr1,
        )

        assert self.tc.new_attr1 == data.attr1
        assert self.tc.attr2 == data.attr2
        assert self.tc.attr3 == data.attr3

    async def upsert_insert(self, session: AsyncSession) -> None:
        data = await self.api.upsert(TRelationORM, session, **self.tc.attrs)
        assert self.tc.attr1 == data.attr1
        assert self.tc.attr2 == data.attr2
        assert self.tc.attr3 == data.attr3

    async def upsert_update(self, session: AsyncSession) -> None:
        data = await self.api.upsert(
            TRelationORM,
            session,
            attr1=self.tc.new_attr1,
            attr2=self.tc.attr2,
            attr3=self.tc.attr3,
        )
        assert self.tc.new_attr1 == data.attr1
        assert self.tc.attr2 == data.attr2
        assert self.tc.attr3 == data.attr3


class BulkAPITest(APIBulkBaseTest):
    async def badd(self, session: AsyncSession):
        data = [tc.attrs for tc in self.tcs]
        await self.api.badd(
            TRelationORM,
            session,
            data=data,
        )

    async def badd_safe(self, session: AsyncSession):
        data = [tc.attrs for tc in self.tcs]
        await self.api.badd(
            TRelationORM,
            session,
            _safe_add=True,
            data=data,
        )

    async def bget_full(self, session: AsyncSession):
        filters_list = [tc.attrs for tc in self.tcs]
        filters = TRelationORM.contact_filters(filters_list)

        data = await self.api.bget(
            TRelationORM,
            session,
            filters=filters,
        )

        for tc in self.tcs:
            records = [r for r in data if r.attr1 == tc.attr1]
            record = records[0] if records else None

            assert record.attr1 == tc.attr1
            assert record.attr2 == tc.attr2
            assert record.attr3 == tc.attr3

    async def bget_part(self, session: AsyncSession):
        filters_list = [tc.attrs for tc in self.tcs]
        filters = TRelationORM.contact_filters(filters_list)

        data = await self.api.bget(
            TRelationORM,
            session,
            attributes=[TRelationORM.attr1],
            filters=filters,
        )

        for tc in self.tcs:
            records = [r for r in data if r.attr1 == tc.attr1]
            record = records[0] if records else None

            assert record.attr1 == tc.attr1
            assert not hasattr(record, "attr2")
            assert not hasattr(record, "attr3")

    async def delete(self, session: AsyncSession):
        await self.api.delete(TRelationORM, session)


async def hand_test():
    test = BasicAPITest(DataBaseAPI(), TEST_CASES[0])
    # test = BulkAPITest(DataBaseAPI(), TEST_CASES)

    await test.test()


async def hand_test_upsert():
    db = DataBaseAPI()

    async with db.session as session:
        id = await db.add(
            TRelationORM,
            session,
            attr1=1,
            attr2=2,
            attr3=3,
            attr4=4,
        )

        await db.upsert(
            TRelationORM,
            session,
            id=id,
            attr1=2,
            attr2=4,
            attr3=9,
            attr4=16,
        )


if __name__ == "__main__":
    asyncio.run(hand_test_upsert())
