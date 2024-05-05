import sys
from typing import Any
from pathlib import Path
from slugify import slugify
from sqlalchemy import create_engine, Engine, select, update
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm import DeclarativeBase, sessionmaker, load_only, Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from settings import settings


class SlugCreationError(Exception):
    pass


class Base(DeclarativeBase):
    pass


def get_sync_engige() -> Engine:
    engine = create_engine(
        url=settings.DSN_psycopg2,
        echo=False,
        pool_size=6,
        max_overflow=12,
    )
    return engine


def get_async_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.DSN_asyncpg,
        echo=False,
        pool_size=6,
        max_overflow=12,
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


class DatabaseORM:
    def __init__(self) -> None:
        if not isinstance(session_factory, async_sessionmaker):
            raise ValueError("Session factory should be asynchronous!")

        self.sf: async_sessionmaker = session_factory
        if not isinstance(self.sf, async_sessionmaker):
            raise TypeError("Sessionmaker is not asynchronous")

    def initiate_slug(
        self,
        text: str,
        created: set[str],
        extra_info: list[object] = [],
    ) -> str:
        if not isinstance(created, (set, dict)):
            raise ValueError("'Created' should be set or dict")

        init_slug = slugify(text)
        slug = init_slug

        for info in extra_info:
            if slug in created:
                slug = init_slug + f"_{info}"
            else:
                return slug

        index = 1
        while slug in created:
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                raise SlugCreationError("Try to create slug >10 times")

        created.add(slug)
        return slug

    @property
    def session(self) -> Session | AsyncSession:
        return self.sf()

    async def exists(self, model: Base, **filters) -> bool:
        query = select(select(model).filter_by(**filters).exists())
        async with self.session as session:
            session: AsyncSession
            exists = await session.scalar(query)
            return exists

    async def slug_exists(
        self,
        slug: str,
        model: Base,
    ) -> bool:
        query = select(select(model).where(model.slug == slug).exists())
        async with self.sf() as session:
            session: AsyncSession
            exists = await session.scalar(query)
            return exists

    async def create_slug(
        self,
        init_slug: str,
        model: Base,
        extra_info: list[object] = [],
    ) -> str:
        if not hasattr(model, "slug"):
            raise AttributeError("Model doesn't contain slug field")

        slug = init_slug
        for info in extra_info:
            if await self.slug_exists(slug, model):
                slug = init_slug + f"_{info}"
            else:
                return slug

        index = 1
        while await self.slug_exists(slug, model):
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                raise SlugCreationError("Try to create slug >10 times")

        return slug

    async def get(
        self,
        table: Base,
        *attributes: list[InstrumentedAttribute],
        **filters: dict[InstrumentedAttribute, Any],
    ) -> list[Base] | list[tuple[Any]]:
        query = select(table)
        if len(attributes) > 0:
            query = select(*attributes)
        if len(filters) > 0:
            query = query.filter_by(**filters)

        async with self.session as session:
            session: AsyncSession
            data = await session.execute(query)
            if len(attributes) > 0:
                return data.all()
            else:
                return data.scalars().all()

    async def insert(
        self,
        record: Base,
    ) -> Base | None:
        try:
            async with self.session as session:
                session: AsyncSession
                session.add(record)

                await session.commit()
                await session.refresh(record)

        except InvalidRequestError as ex:
            print(ex)

        finally:
            return record

    async def goc(
        self,
        instance: Base,
        model: Base,
        **filters,
    ) -> list[Base]:
        """Get or Create method"""

        ## TODO: check optimization problem
        ## brute-force insertion with try/except
        ## without checking existance of record

        ## for now it isn't necessary because we
        ## don't use old try/except

        if await self.exists(model, **filters):
            record = await self.get(model, **filters)
            if isinstance(record, list):
                record = record[0]

        else:
            record = await self.insert(instance)

            # try:
            #     record = await self.insert(instance)

            # except IntegrityError:
            #     record = await self.get(model, **filters)
            #     if isinstance(record, list):
            #         record = record[0]

        return record

    async def update(
        self,
        model: Base,
        filters: dict[InstrumentedAttribute, Any],
        **updates: dict[InstrumentedAttribute, Any],
    ) -> None:
        query = update(model).filter_by(**filters).values(**updates)

        async with self.session as session:
            session: AsyncSession
            await session.execute(query)
            await session.commit()


_MAIN_ENGINE = get_async_engine

get_engine = _MAIN_ENGINE
engine = get_engine()
session_factory = get_sessionfactory(engine)
