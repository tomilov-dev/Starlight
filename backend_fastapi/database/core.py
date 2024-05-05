import sys
import hashlib
from typing import Any
from pathlib import Path
import dataclasses
from slugify import slugify
from sqlalchemy import create_engine, Engine, select, update, insert, inspect
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    load_only,
    Session,
    object_session,
)
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


def generate_short_hash(text: str, length: int) -> str:
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    return sha256_hash[:length]


def as_dict(obj: Base) -> dict:
    data = {}
    for c in inspect(obj).mapper.column_attrs:
        attr_data = getattr(obj, c.key)
        if attr_data is not None:
            data[c.key] = attr_data
    return data


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
        hash_slug = False

        while slug in created:
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                if not hash_slug:
                    uniq_value = generate_short_hash(init_slug, 8)
                    slug = init_slug + f"_{uniq_value}"
                    hash_slug = True
                else:
                    raise SlugCreationError("Try to create slug >10 times")

        created.add(slug)
        return slug

    @property
    def session(self) -> Session | AsyncSession:
        return self.sf()

    async def exists(
        self,
        model: Base,
        session: AsyncSession,
        **filters,
    ) -> bool:
        query = select(select(model).filter_by(**filters).exists())
        exists = await session.scalar(query)
        return exists

    async def slug_exists(
        self,
        slug: str,
        model: Base,
        session: AsyncSession,
    ) -> bool:
        exists = await self.exists(model, session, slug=slug)
        return exists

    async def create_slug(
        self,
        init_slug: str,
        model: Base,
        session: AsyncSession,
        extra_info: list[object] = [],
    ) -> str:
        if not hasattr(model, "slug"):
            raise AttributeError("Model doesn't contain slug field")

        slug = init_slug
        for info in extra_info:
            if await self.slug_exists(slug, model, session):
                slug = init_slug + f"_{info}"
            else:
                return slug

        index = 1
        while await self.slug_exists(slug, model, session):
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                if not hash_slug:
                    uniq_value = generate_short_hash(init_slug, 8)
                    slug = init_slug + f"_{uniq_value}"
                    hash_slug = True
                else:
                    raise SlugCreationError("Try to create slug >10 times")

        return slug

    async def get(
        self,
        table: Base,
        session: AsyncSession,
        *attributes: list[InstrumentedAttribute],
        **filters: dict[InstrumentedAttribute, Any],
    ) -> list[Base] | list[tuple[Any]]:
        query = select(table)
        if len(attributes) > 0:
            query = select(*attributes)
        if len(filters) > 0:
            query = query.filter_by(**filters)

        data = await session.execute(query)
        if len(attributes) > 0:
            return data.all()
        else:
            return data.scalars().all()

    async def insert(
        self,
        record: Base,
        session: AsyncSession,
        flush: bool = False,
    ) -> None:
        session.add(record)
        if flush:
            await session.flush()

    async def goc(
        self,
        instance: Base,
        model: Base,
        session: AsyncSession,
        **filters,
    ) -> list[Base]:
        """Get or Create method"""

        if await self.exists(model, session, **filters):
            instance = await self.get(model, session, **filters)
            if isinstance(instance, list):
                instance = instance[0]

        else:
            try:
                await self.insert(instance, session)
                await session.commit()
                await session.refresh(instance)

            except IntegrityError:
                instance = await self.get(model, session, **filters)
                if isinstance(instance, list):
                    instance = instance[0]

        return instance

    async def update(
        self,
        model: Base,
        session: AsyncSession,
        filters: dict[InstrumentedAttribute, Any],
        flush: bool = False,
        **updates: dict[InstrumentedAttribute, Any],
    ) -> None:
        query = update(model).filter_by(**filters).values(**updates)
        await session.execute(query)
        if flush:
            await session.flush()


_MAIN_ENGINE = get_async_engine

get_engine = _MAIN_ENGINE
engine = get_engine()
session_factory = get_sessionfactory(engine)
