import sys
import asyncio
from pathlib import Path
from typing import Type, Any, Generator

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm.attributes import InstrumentedAttribute

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

from movies.orm import IMDbMovieORM
from core import BaseORM, session_factory
from interfaces import (
    AbstractDataBaseBacisAPI,
    AbstractDataBaseBulkAPI,
    AbstractDataBaseManyAPI,
)


class MaxBatchSizeExceeded(ValueError):
    def __init__(
        self,
        message: str = "MAX_BATCH_SIZE exceeded",
    ) -> None:
        self.message = message
        super().__init__(self.message)


class ExceptionToHandle:
    def __init__(
        self,
        exception: Exception,
        clarification_str: str | None = None,
    ):
        self.exception = exception
        self.clarification_str = clarification_str

    def handle(
        self,
        exc: Exception,
    ) -> bool:
        if isinstance(exc, self.exception):
            if self.clarification_str and hasattr(exc, "orig"):
                if self.clarification_str in str(exc.orig):
                    self.handle_status(exc)
                    return True
                return False
            self.handle_status(exc)
            return True
        return False

    def handle_status(self, exc) -> None:
        print("Exception handled:", exc)


class ExceptionHandler:
    def __init__(
        self,
        error_handlers: list[ExceptionToHandle],
    ) -> None:
        self.error_handlers = tuple(error_handlers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type and any(h.handle(exc) for h in self.error_handlers):
            return True
        return False


class DataBaseBasicAPI(AbstractDataBaseBacisAPI):
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
    ) -> BaseORM | None:
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
        _commit: bool = True,
        **data: Any,
    ) -> int | None:
        """
        Insert data in database.
        Return id of the created object or None.
        """

        query = Insert(table).values(**data)
        query = query.on_conflict_do_nothing() if _safe_add else query
        query = query.returning(table.id)

        id = await session.execute(query)
        if _commit:
            await session.commit()

        id = id.first()
        id = id[0] if id else None
        return id

    async def goc(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        _commit: bool = True,
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
            if _commit:
                await session.commit()
            return result

        return await self.get(table, session, **data)

    async def update(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        filters: dict[str, Any],
        _commit: bool = True,
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

        if _commit:
            await session.commit()
        return updated

    async def upsert(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        conflict_attributes: list[str] = ["id"],
        **data: Any,
    ) -> BaseORM:
        """
        Update or Insert method.
        Return the record.
        """

        if not conflict_attributes:
            conflict_attributes = ["id"]

        dset = {k: v for k, v in data.items() if k != "id"}
        query = Insert(table).values(**data)
        query = query.on_conflict_do_update(
            index_elements=conflict_attributes,
            set_=dset,
        )
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

        query = delete(table)
        query = query.filter_by(**filters) if filters else query
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


class DataBaseManyAPI(AbstractDataBaseManyAPI):
    async def mget(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        *attributes: InstrumentedAttribute,
        **filters: Any,
    ) -> list[BaseORM] | None:
        query = select(*attributes) if attributes else select(table)
        query = query.filter_by(**filters) if filters else query

        data = await session.execute(query)
        if attributes:
            return data.all()
        return data.scalars().all()

    async def madd(self):
        raise NotImplementedError()


class DataBaseBulkAPI(AbstractDataBaseBulkAPI):
    async def bget(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        attributes: list[InstrumentedAttribute] = [],
        filters: dict[str, list[Any]] = {},
    ) -> list[BaseORM] | None:
        if not filters:
            raise ValueError("You should pass at least one filter")

        query = select(*attributes) if attributes else select(table)
        for key, value in filters.items():
            attr = getattr(table, key)
            query = query.filter(attr.in_(value))

        data = await session.execute(query)
        if attributes:
            return data.all()
        return data.scalars().all()

    async def badd(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
        _safe_add: bool = False,
        data: list[dict[str, Any]] = [],
    ) -> None:
        """Insert batch of objects in database"""

        if not data:
            return None

        query = Insert(table).values(data)
        query = query.on_conflict_do_nothing() if _safe_add else query

        await session.execute(query)
        await session.commit()


class DataBaseAPI(
    DataBaseBasicAPI,
    DataBaseManyAPI,
    DataBaseBulkAPI,
):
    @property
    def session(self) -> AsyncSession:
        return session_factory()


async def test():
    db = DataBaseAPI()

    async with db.session as session:
        exist = await db.exists(
            IMDbMovieORM,
            session,
            slug="the-shawshank-redemption",
        )
        print(exist)


if __name__ == "__main__":
    asyncio.run(test())
