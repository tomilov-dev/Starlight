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


class AbstractDataBaseManyAPI(ABC):
    """
    Low Level Basic Api.
    Contains default CRUD operations.
    All methods require session.
    """

    @abstractmethod
    async def mget(
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
    async def madd(
        self,
        session: AsyncSession,
    ) -> None:
        """
        Insert data in database.
        Return None.
        """

        pass


class AbstractDataBaseBulkAPI(ABC):
    """
    Low Level Bulk Api.
    Contains bulk CRUD operations.
    All methods require session.
    """

    @abstractmethod
    async def bget(
        self,
        session: AsyncSession,
    ) -> None:
        """Insert object in database"""

        pass

    @abstractmethod
    async def badd(
        self,
        session: AsyncSession,
    ) -> None:
        """Insert object in database"""

        pass
