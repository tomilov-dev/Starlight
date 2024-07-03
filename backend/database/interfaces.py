import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(Path(__file__).parent))

from core import BaseORM, session_factory


class AbstractDataBaseBacisAPI(ABC):
    """
    Low Level Basic Api.
    Contains default CRUD operations.
    All methods require session.
    """

    @abstractmethod
    async def get(
        self,
        table: Type[BaseORM],
        session: AsyncSession,
    ) -> list[BaseORM] | None:
        """
        Get data from specified table.
        Return list of records or None.
        """

        pass

    @abstractmethod
    async def add(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Insert data in database.
        Return None.
        """

        pass

    @abstractmethod
    async def goc(
        self,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Get or Create method.
        Return the record.
        """

        pass

    @abstractmethod
    async def update(
        self,
        session: AsyncSession,
    ) -> BaseORM | None:
        """
        Update method.
        Return the record or None.
        """

        pass

    @abstractmethod
    async def upsert(
        self,
        session: AsyncSession,
    ) -> BaseORM:
        """
        Update or Insert method.
        Return the record.
        """

        pass

    @abstractmethod
    async def delete(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Delete method.
        Return None.
        """

        pass

    @abstractmethod
    async def exists(
        self,
        session: AsyncSession,
    ) -> bool:
        """
        Check if data exists in the database.
        Return boolean.
        """

        pass


class AbstractDataBaseBulkAPI(ABC):
    """
    Low Level Bulk Api.
    Contains bulk CRUD operations.
    All methods require session.
    """

    @abstractmethod
    async def badd(
        self,
        session: AsyncSession,
    ) -> None:
        """Insert object in database"""

        pass

    @abstractmethod
    async def bgoc(
        self,
        session: AsyncSession,
    ) -> BaseORM:
        """Get or Create method: return the object"""

        pass

    @abstractmethod
    async def bupdate(
        self,
        session: AsyncSession,
    ):
        """Update method"""

        pass

    @abstractmethod
    async def bupsert(
        self,
        session: AsyncSession,
    ):
        """Update or insert method"""

        pass

    @abstractmethod
    async def bexists(
        self,
        session: AsyncSession,
    ):
        """Check if the object exists in the database"""

        pass


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
