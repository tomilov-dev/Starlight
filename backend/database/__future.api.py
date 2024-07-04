import sys
from pathlib import Path
from typing import Type, Any
from abc import ABC, abstractmethod

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.orm.attributes import InstrumentedAttribute

sys.path.append(str(Path(__file__).parent))

from core import BaseORM, session_factory
from api import DataBaseBasicAPI, DataBaseBulkAPI


class AbstractDataBaseRecordAPI(ABC):
    """
    Low Level Record Api.
    Contains CRUD operations with records.
    All methods require session.
    """

    @abstractmethod
    async def radd(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> None:
        """
        Insert the record in the database.
        Return None.
        """

        pass

    @abstractmethod
    async def rgoc(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Get or Create method.
        Return the record.
        """

        pass

    @abstractmethod
    async def rupdate(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM | None:
        """
        Update method.
        Return the record or None.
        """

        pass

    @abstractmethod
    async def rupsert(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Update or Insert method.
        Return the record.
        """

        pass

    @abstractmethod
    async def rdelete(
        self,
        record: BaseORM,
        session: AsyncSession,
    ) -> None:
        """
        Delete method.
        Return None.
        """

        pass

    @abstractmethod
    async def rexists(
        self,
        record: BaseORM,
        session: AsyncSession,
    ):
        """
        Check if the record exists in the database.
        Return boolean.
        """

        pass


class AbstractDataBaseBulkRecordAPI(ABC):
    """
    Low Level Many Bulk Record Api.
    Contains bulk CRUD operations with records.
    All methods require session.
    """

    @abstractmethod
    async def brget(
        self,
        session: AsyncSession,
    ) -> list[BaseORM]:
        """Get data from specified table"""

        pass

    @abstractmethod
    async def bradd(
        self,
        session: AsyncSession,
    ) -> None:
        """Insert object in database"""

        pass

    @abstractmethod
    async def brgoc(
        self,
        session: AsyncSession,
    ) -> BaseORM:
        """Get or Create method: return the object"""

        pass

    @abstractmethod
    async def brupdate(
        self,
        session: AsyncSession,
    ):
        """Update method"""

        pass

    @abstractmethod
    async def brupsert(
        self,
        session: AsyncSession,
    ):
        """Update or insert method"""

        pass

    @abstractmethod
    async def brdelete(
        self,
        session: AsyncSession,
    ):
        """Detele method"""

        pass

    @abstractmethod
    async def brexists(
        self,
        session: AsyncSession,
    ):
        """Check if the object exists in the database"""

        pass


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
