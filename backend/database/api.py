"""Low Level API"""

import sys
import asyncio
from pathlib import Path
from typing import Any, Generator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.dialects.postgresql import Insert

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import DatabaseCoreORM, Base

from asyncpg.exceptions import UniqueViolationError

MAX_BATCH_SIZE = 1000


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


class ErrorHandler:
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


class DatabaseORM(DatabaseCoreORM):
    """SQLAlchemy async DB API"""

    pass


class DatabaseBatchORM(DatabaseORM):
    """SQLAlchemy async DB API with batch load support"""

    def batching(
        self,
        array: list[object],
    ) -> Generator[Any, Any, list[object]]:
        """Divide the array in batches"""

        for i in range(0, len(array), MAX_BATCH_SIZE):
            yield array[i : i + MAX_BATCH_SIZE]

    async def __insert_batch(
        self,
        batch: list[Base],
        session: AsyncSession,
        flush: bool = False,
    ) -> None:
        """Async Batch Insertion: one batch upload"""

        session.add_all(batch)
        await session.commit()
        if flush:
            await session.flush()

    async def insertb_r(
        self,
        records: list[Base],
        session: AsyncSession,
        flush: bool = False,
    ) -> None:
        """Async Batch Insertion: divide the array in batches and upload 'em"""

        tasks = [
            asyncio.create_task(self.__insert_batch(b, session, flush))
            for b in self.batching(records)
        ]
        await asyncio.gather(*tasks)

    async def __goc_batch(
        self,
        table: Base,
        batch: list[Base],
        session: AsyncSession,
    ) -> None:
        data = [
            {
                column.name: getattr(record, column.name)
                for column in table.__table__.columns
                if not (column.name == "id" and getattr(record, column.name) is None)
            }
            for record in batch
        ]

        statement = Insert(table).values(data)
        statement = statement.on_conflict_do_nothing()
        await session.execute(statement)
        await session.commit()

    async def gocb_r(
        self,
        records: list[Base],
        session: AsyncSession,
        filter_field: InstrumentedAttribute = None,
        filter_keys: list[Any] = None,
    ) -> list[Base] | None:
        table = type(records[0])
        tasks = [
            asyncio.create_task(self.__goc_batch(table, b, session))
            for b in self.batching(records)
        ]
        await asyncio.gather(*tasks)

        if filter_field is None or filter_keys is None:
            return None

        query = select(table).where(filter_field.in_(filter_keys))
        result = await session.execute(query)
        return result.scalars().all()


class DatabaseAPI(DatabaseBatchORM):
    """Main Database API methods. It's Singleton"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
