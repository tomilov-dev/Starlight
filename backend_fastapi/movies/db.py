import sys
import asyncio
from pathlib import Path
from typing import Any, Generator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import DatabaseORM
from movies.orm import Base


MAX_BATCH_SIZE = 500


class MaxBatchSizeExceeded(ValueError):
    def __init__(
        self,
        message: str = "MAX_BATCH_SIZE exceeded",
    ) -> None:
        self.message = message
        super().__init__(self.message)


class MovieDatabaseORM(DatabaseORM):
    """SQLAlchemy async DB API"""

    pass


class MovieDatabaseBatchORM(MovieDatabaseORM):
    """SQLAlchemy async DB API with batch load support"""

    def batching(
        self,
        array: list[object],
    ) -> Generator[Any, Any, Any]:
        """Divide the array in batches"""

        for i in range(0, len(array), MAX_BATCH_SIZE):
            yield array[i : i + MAX_BATCH_SIZE]

    async def upload_batch(
        self,
        batch: list[Base],
        session: AsyncSession,
        flush: bool = False,
    ) -> None:
        """Async Batch Insertion: one batch upload"""

        session.add_all(batch)
        if flush:
            await session.flush()

    async def insertb(
        self,
        array: list[Base],
        session: AsyncSession,
        flush: bool = True,
    ) -> None:
        """Async Batch Insertion: divide the array in batches and upload 'em"""

        tasks = [self.upload_batch(b, session, flush) for b in self.batching(array)]
        await asyncio.gather(*tasks)


class MovieDatabaseRaw:
    """Raw async DBAPI"""

    async def insert_imdb(self):
        pass

    async def insertb_imdb(self):
        pass


class MovieDatabase(MovieDatabaseBatchORM):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
