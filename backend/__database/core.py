import sys
import asyncio
from typing import Any
from pathlib import Path
from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import create_engine, Engine, select, update, insert, inspect
from sqlalchemy.exc import IntegrityError, InvalidRequestError, NoResultFound
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    load_only,
    Session,
    object_session,
)
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from settings import settings


class Base(DeclarativeBase):
    @classmethod
    def from_pydantic(cls, pydantic: BaseModel) -> "Base":
        allowed_attributes = set(cls.__table__.columns.keys())
        pydantic_data = pydantic.model_dump().items()
        return cls(
            **{key: value for key, value in pydantic_data if key in allowed_attributes}
        )


def get_sync_engige() -> Engine:
    engine = create_engine(
        url=settings.DSN_psycopg3,
        echo=settings.DEBUG,
        pool_size=settings.PG_POOL_SIZE,
        max_overflow=settings.PG_MAX_OVERFLOW,
    )
    return engine


def get_async_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.DSN_asyncpg,
        echo=settings.DEBUG,
        pool_size=settings.PG_POOL_SIZE,
        max_overflow=settings.PG_MAX_OVERFLOW,
    )
    return engine


def get_sessionfactory(
    engine: Engine | AsyncEngine,
) -> sessionmaker | async_sessionmaker:
    if isinstance(engine, Engine):
        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    elif isinstance(engine, AsyncEngine):
        session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    else:
        raise ValueError("Passed wrong ORM Engine")

    return session_factory


def as_dict(obj: Base) -> dict:
    data = {}
    for c in inspect(obj).mapper.column_attrs:
        attr_data = getattr(obj, c.key)
        if attr_data is not None:
            data[c.key] = attr_data
    return data


_MAIN_ENGINE = get_async_engine

get_engine = _MAIN_ENGINE
engine = get_engine()
session_factory = get_sessionfactory(engine)


class SessionHandler:
    def __init__(
        self,
        session: AsyncSession | None = None,
    ) -> None:
        self.__session_created: bool = False
        if session and not isinstance(session, AsyncSession):
            raise ValueError(f"Session should be AsyncSession. Passed: {session}")

        self.session = session

    async def __aenter__(self):
        if self.session is None:
            self.session = session_factory()
            self.__session_created = True
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if self.__session_created:
            task = asyncio.create_task(self.session.close())
            await asyncio.shield(task)
            self.__session_created = False

        if exc_type:
            return False
        return True


class DatabaseCoreORM:
    """Core methods of Database API"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self) -> None:
        if not isinstance(session_factory, async_sessionmaker):
            raise ValueError("Session factory should be asynchronous!")
        self.session_factory = session_factory

    def session(self, session: AsyncSession | None = None) -> AsyncSession:
        return SessionHandler(session)

    async def exists(
        self,
        table: Base,
        session: AsyncSession,
        **filters: dict[str, Any],
    ) -> bool:
        """
        Check existance of data in the table by filters

        1. Need to pass table (ORM model). Not record.
        2. Need to pass session.
        3. Need to pass AT LEAST ONE filter
        """

        if filters == {} or not filters:
            raise ValueError(
                "Need to pass at least one filter for check data existence"
            )

        query = select(select(table).filter_by(**filters).exists())
        return await session.scalar(query)

    async def exists_r(
        self,
        record: Base,
        session: AsyncSession,
    ) -> bool:
        """
        Check existance of the record in the table by their attributes

        1. Need to pass record (instance of ORM model).
        2. Need to pass session.
        """

        table = type(record)
        filters = {
            column.name: getattr(record, column.name)
            for column in table.__table__.columns
            if getattr(record, column.name) is not None
        }
        query = select(select(table).filter_by(**filters).exists())
        return await session.scalar(query)

    async def get(
        self,
        table: Base,
        session: AsyncSession,
        *attributes: list[InstrumentedAttribute],
        **filters: dict[str, Any],
    ) -> list[Base] | list[tuple[Any]]:
        """
        Get data from table usings passed filters.
        Retrieves only passed attributes.
        If attributes aren't passed, all attributes are retrived.

        1. Need to pass table (ORM model). Not record.
        2. Need to pass session.
        3. Need to pass AT LEAST ONE filter.

        Return list of Model Records or Part of Model Records (namedtuple)
        """

        query = select(table)
        if len(attributes) > 0:
            query = select(*attributes)
        if len(filters) > 0:
            query = query.filter_by(**filters)

        data = await session.execute(query)
        if len(attributes) == 0:
            data = data.scalars()
        return data.all()

    async def insert(
        self,
        record: Base,
        session: AsyncSession,
        flush: bool = True,
    ) -> None:
        """Insert and Flush (object update) method"""

        session.add(record)
        if flush:
            await session.flush()
        await session.commit()

    async def insertcr(
        self,
        record: Base,
        session: AsyncSession,
        refresh: bool = True,
    ) -> None:
        """Insert, Commit and Refresh method"""

        session.add(record)
        await session.commit()
        if refresh:
            await session.refresh(record)

    async def goc_r(
        self,
        record: Base,
        session: AsyncSession,
    ) -> Base:
        table = type(record)
        data = {
            column.name: getattr(record, column.name)
            for column in table.__table__.columns
            if not (column.name == "id" and getattr(record, column.name) is None)
        }

        insert_stmt = Insert(table).values(**data)
        do_nothing_stmt = insert_stmt.on_conflict_do_nothing()
        returning = do_nothing_stmt.returning(*table.__table__.columns)

        result = await session.execute(returning)
        await session.commit()
        return result.fetchone()

    async def update_r(
        self,
        record: Base,
        session: AsyncSession,
    ) -> Base | None:
        raise NotImplementedError("update_r is not implemented")

    async def update(
        self,
        table: Base,
        session: AsyncSession,
        filters: dict[str, Any],
        flush: bool = False,
        **updates: dict[str, Any],
    ) -> None:
        query = update(table).filter_by(**filters).values(**updates)
        await session.execute(query)
        if flush:
            await session.flush()
        await session.commit()
