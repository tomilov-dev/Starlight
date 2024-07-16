import sys
import asyncio
from typing import Any, Type
from pathlib import Path
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from sqlalchemy import create_engine, Engine, select, update, insert, inspect
from sqlalchemy.exc import IntegrityError, InvalidRequestError, NoResultFound
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import DeclarativeBase, sessionmaker
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


intpk = Annotated[int, mapped_column(primary_key=True)]


class BaseORM(DeclarativeBase):
    id: Mapped[intpk]

    @classmethod
    def from_pydantic(cls, pydantic: BaseModel) -> "BaseORM":
        allowed_attributes = set(cls.__table__.columns.keys())
        pydantic_data = pydantic.model_dump().items()
        return cls(
            **{key: value for key, value in pydantic_data if key in allowed_attributes}
        )

    @classmethod
    def contact_filters(
        cls,
        filters_list: list[dict[str, Any]],
    ) -> dict[str, Any]:
        filters = {}
        for orm_filter in filters_list:
            for key, value in orm_filter.items():
                if key in filters:
                    filters[key].append(value)
                else:
                    filters[key] = [value]
        return filters

    @property
    def table(self) -> Type["BaseORM"]:
        return type(self)

    @property
    def excluded_attrs(self) -> set[str]:
        return set(["id"])

    def filters(self) -> dict:
        filters = {}

        for column in inspect(self).mapper.column_attrs:
            attr_data = getattr(self, column.key)
            if attr_data is not None:
                filters[column.key] = attr_data

        return filters

    def to_dict(self) -> dict:
        data = {}

        excluded_attrs = self.excluded_attrs
        for column in inspect(self).mapper.column_attrs:
            if column.key in excluded_attrs:
                continue

            attr_data = getattr(self, column.key)
            if attr_data is not None:
                data[column.key] = attr_data

        return data


class TRelationORM(BaseORM):
    """Test Relation"""

    __tablename__ = "__test_relation"

    id: Mapped[intpk]

    attr1: Mapped[int]
    attr2: Mapped[int]
    attr3: Mapped[int]
    attr4: Mapped[int | None]

    __table_args__ = (
        UniqueConstraint("attr1"),
        UniqueConstraint("attr2"),
        UniqueConstraint("attr3"),
    )

    def __repr__(self) -> str:
        return f"Object.attr1={self.attr1}"


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
