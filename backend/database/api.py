import sys
from pathlib import Path
from typing import Type, Any

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm.attributes import InstrumentedAttribute

sys.path.append(str(Path(__file__).parent))

from core import BaseORM, session_factory
from interfaces import (
    AbstractDataBaseBacisAPI,
    AbstractDataBaseBulkAPI,
    AbstractDataBaseBulkRecordAPI,
    AbstractDataBaseRecordAPI,
)


class DataBaseBasicAPI(
    AbstractDataBaseBacisAPI,
):
    """
    Low Level Basic Api.
    Contains default CRUD operations.
    All methods require session.
    """

    async def get(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        *attributes: InstrumentedAttribute,
        **filters: Any,
    ) -> list[BaseORM] | None:
        """
        Get data from specified table.
        Return list of records or None.
        """

        query = select(*attributes) if attributes else select(table)
        query = query.filter_by(**filters) if filters else query

        data = await session.execute(query)
        if attributes:
            return data.first()
        return data.scalars().first()

    async def add(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        _safe_add: bool = False,
        **data: Any,
    ) -> int | None:
        """
        Insert data in database.
        Return None.
        """

        query = Insert(table).values(**data)
        query = query.on_conflict_do_nothing() if _safe_add else query
        query = query.returning(table.id)

        id = await session.execute(query)
        await session.commit()
        return id

    async def goc(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        **data: Any,
    ) -> BaseORM:
        """
        Get or Create method.
        Return the record.
        """

        query = Insert(table).values(**data)
        query = query.on_conflict_do_nothing()
        query = query.returning(*table.__table__.columns)

        result = await session.execute(query)
        result = result.fetchone()

        if result:
            await session.commit()
            return result

        return await self.get(table, session, **data)

    async def update(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        filters: dict[str, Any],
        **updates: Any,
    ) -> BaseORM | None:
        """
        Update method.
        Return the record or None.
        """

        query = update(table).filter_by(**filters)
        query = query.values(**updates)
        query = query.returning(*table.__table__.columns)

        updated = await session.execute(query)
        updated = updated.fetchone()

        await session.commit()
        return updated

    async def upsert(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        **data: Any,
    ) -> BaseORM:
        """
        Update or Insert method.
        Return the record.
        """

        raise NotImplementedError()

        query = Insert(table).values(**data)
        query = query.on_conflict_do_update()
        query = query.returning(*table.__table__.columns)

        result = await session.execute(query)
        result = result.fetchone()

        await session.commit()
        return result

    async def delete(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        **filters: Any,
    ) -> None:
        """
        Delete method.
        Return None.
        """

        query = delete(table).filter_by(**filters)
        await session.execute(query)
        await session.commit()

    async def exists(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        **filters: Any,
    ) -> bool:
        """
        Check if data exists in the database.
        Return boolean.
        """

        query = select(select(table).filter_by(**filters).exists())
        return await session.scalar(query)


class DataBaseRecordAPI(
    AbstractDataBaseRecordAPI,
    DataBaseBasicAPI,
):
    """
    Low Level Record Api Implementation.
    Contains CRUD operations with records.
    All methods require session.
    """

    async def radd(
        self,
        record: BaseORM,
        session: AsyncSession,
        refresh: bool = True,
    ) -> None:
        """
        Insert the record in the database.
        Return None.
        """

        session.add(record)
        await session.commit()
        if refresh:
            await session.refresh(record)

    async def rgoc(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Get or Create method.
        Return the record.
        """

        return await self.goc(
            record.table,
            session,
            **record.to_dict(),
        )

    async def rupdate(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM | None:
        """
        Update method.
        Return the record or None.
        """

        raise NotImplementedError()

    async def rupsert(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Update or Insert method.
        Return the record.
        """

        raise NotImplementedError()

    async def rdelete(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> None:
        """
        Delete method.
        Return None.
        """

        await self.delete(record.table, session, **record.filters())
        await session.commit()

    async def rexists(
        self,
        record: BaseORM,
        session: AsyncSession,
    ):
        """
        Check if the record exists in the database.
        Return boolean.
        """

        table = record.table
        filters = record.filters()

        query = select(select(table).filter_by(**filters).exists())
        return await session.scalar(query)


class DataBaseBulkAPI(
    AbstractDataBaseBulkAPI,
):
    async def badd(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        data: list[dict[str, Any]],
    ) -> None:
        """Insert object in database"""

        if not data:
            return None

        query = insert(table).values(data)
        await session.execute(query)
        await session.commit()

    async def bgoc(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        data: list[dict[str, Any]],
    ) -> BaseORM:
        """Get or Create method: return the object"""

        if not data:
            return None

        query = Insert(table).values(data)
        query = query.on_conflict_do_nothing()
        query = query.returning(*table.__table__.columns)

        result = await session.execute(query)
        await session.commit()
        return result.fetchone()

    async def bupdate(
        self,
        session: AsyncSession,
    ):
        """Update method"""

        pass

    async def bupsert(
        self,
        session: AsyncSession,
    ):
        """Update or insert method"""

        pass

    async def bexists(
        self,
        session: AsyncSession,
    ):
        """Check if the object exists in the database"""

        pass


class DatabaseBulkRecordAPI(
    AbstractDataBaseBulkRecordAPI,
    DataBaseBulkAPI,
):

    async def brget(
        self,
        session: AsyncSession,
    ) -> list[BaseORM]:
        """Get data from specified table"""

        raise NotImplementedError()

    async def bradd(
        self,
        session: AsyncSession,
    ) -> None:
        """Insert object in database"""

        raise NotImplementedError()

    async def brgoc(
        self,
        session: AsyncSession,
    ) -> BaseORM:
        """Get or Create method: return the object"""

        raise NotImplementedError()

    async def brupdate(
        self,
        session: AsyncSession,
    ):
        """Update method"""

        raise NotImplementedError()

    async def brupsert(
        self,
        session: AsyncSession,
    ):
        """Update or insert method"""

        raise NotImplementedError()

    async def brdelete(
        self,
        session: AsyncSession,
    ):
        """Detele method"""

        raise NotImplementedError()

    async def brexists(
        self,
        session: AsyncSession,
    ):
        """Check if the object exists in the database"""

        raise NotImplementedError()


class DataBaseAPI(
    DataBaseBulkAPI,
    DataBaseRecordAPI,
):
    @property
    def session(self) -> AsyncSession:
        return session_factory()
