import sys
import asyncio
import hashlib
from typing import Any
from pathlib import Path
from abc import abstractmethod
from slugify import slugify
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import InstrumentedAttribute


ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))


from database.core import Base, SessionHandler
from database.api import DatabaseAPI, ErrorHandler, ExceptionToHandle


class SlugCreationError(Exception):
    pass


def generate_short_hash(text: str, length: int) -> str:
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    return sha256_hash[:length]


class Slugger:
    def __init__(
        self,
        manager: "DatabaseManager",
        upload_slugs_from_db: bool = False,
    ) -> None:
        self.manager = manager
        self.upload_slugs_from_db = upload_slugs_from_db

        self.created_slugs = set()

    async def setup(self, slugs_from_db: list[str] | set[str]) -> None:
        self.created_slugs = set()
        if slugs_from_db:
            self.created_slugs.update(set(slugs_from_db))
        else:
            if self.upload_slugs_from_db:
                slugs_from_db = await self.manager.get(self.manager.ORM.slug)
                self.created_slugs.update(slugs_from_db)

    def clear(self) -> None:
        self.created_slugs = set()

    def initiate_slug(
        self,
        text: str,
        extra_info: list[object] = [],
    ) -> str:
        init_slug = slugify(text)
        slug = init_slug

        for info in extra_info:
            if slug in self.created_slugs:
                slug = init_slug + f"_{info}"
            else:
                return slug

        index = 1
        hash_slug = False

        while slug in self.created_slugs:
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                if not hash_slug:
                    uniq_value = generate_short_hash(init_slug, 8)
                    slug = init_slug + f"_{uniq_value}"
                    hash_slug = True
                else:
                    raise SlugCreationError("Try to create slug >10 times")

        self.created_slugs.add(slug)
        return slug

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
            if await self.manager.dbapi.exists(model, session, slug=slug):
                slug = init_slug + f"_{info}"
            else:
                return slug

        index = 1
        while await self.manager.dbapi.exists(model, session, slug=slug):
            slug = init_slug + f"_{index}"
            index += 1

            if index >= 11:
                if not hash_slug:
                    uniq_value = generate_short_hash(init_slug, 8)
                    slug = init_slug + f"_{uniq_value}"
                    hash_slug = True
                else:
                    raise SlugCreationError("Try to create slug >10 times")

        self.created_slugs.add(slug)
        return slug


class AbstractDatabaseManager:
    ORM: Base = None

    def __init__(self) -> None:
        self.dbapi = DatabaseAPI()

        if self.ORM is None:
            raise AttributeError("You should pass ORM to manager class")

    @abstractmethod
    async def get(
        self,
        table: Base,
        *attributes: list[InstrumentedAttribute],
        sess: AsyncSession | None = None,
        **filters: dict[InstrumentedAttribute, Any],
    ) -> list[Base] | list[tuple[Any]]:
        pass

    @abstractmethod
    async def goc(
        self,
        object: BaseModel,
        sess: AsyncSession | None = None,
    ) -> Base:
        """Implement GoC method"""

        pass

    @abstractmethod
    async def goc_many(
        self,
        objects: list[BaseModel],
        sess: AsyncSession | None = None,
    ) -> Base:
        """Implement GoC method for bunch of objects"""

        pass

    @abstractmethod
    async def add(
        self,
        object: BaseModel,
        sess: AsyncSession | None = None,
    ) -> Base:
        """Implement Insert method"""

        pass

    @abstractmethod
    async def add_many(
        self,
        objects: list[BaseModel],
    ) -> list[Base]:
        """Implement Insert method for bunch of objects"""

        pass

    @abstractmethod
    async def add_batch(
        self,
        objects: list[BaseModel],
    ) -> None:
        """Implement Batch Insertion"""

        pass

    ## Future Methods
    async def delete(
        self,
        object: Base,
        sess: AsyncSession | None = None,
    ) -> None:
        pass

    async def update(
        self,
        object: Base,
        sess: AsyncSession | None = None,
    ) -> None:
        pass


class DatabaseManager(AbstractDatabaseManager):
    """Provide Default methods behavior"""

    def __init__(
        self,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__()

        self.slugger = Slugger(self)
        self.error_handler = ErrorHandler(exceptions_to_handle)

    async def get(
        self,
        *attributes: list[InstrumentedAttribute],
        table_model: Base | None = None,
        sess: AsyncSession | None = None,
        **filters: dict[str, Any],
    ) -> list[Base] | list[tuple[Any]]:
        table_model = self.ORM if table_model is None else table_model
        async with self.dbapi.session(sess) as session:
            return await self.dbapi.get(
                table_model,
                session,
                *attributes,
                **filters,
            )

    async def goc(
        self,
        object: BaseModel,
        sess: AsyncSession | None = None,
    ) -> Base:
        """Default Implementation: Get or Create the object"""

        orm = self.ORM.from_pydantic(object)
        async with self.dbapi.session(sess) as session:
            return await self.dbapi.goc_r(orm, session)

    async def goc_many(
        self,
        objects: list[BaseModel],
        sess: AsyncSession | None = None,
        **filters,
    ) -> Base:
        async with self.dbapi.session(sess) as session:
            tasks = [
                asyncio.create_task(self.goc(obj, session, **filters))
                for obj in objects
            ]
            return await asyncio.gather(*tasks)

    async def add(
        self,
        object: BaseModel | Base,
        sess: AsyncSession | None = None,
    ) -> Base | None:
        """Default Implementation: Try to Insert the object"""

        orm = object
        if isinstance(object, BaseModel):
            orm = self.ORM.from_pydantic(object)

        async with self.dbapi.session(sess) as session:
            async with self.error_handler:
                await self.dbapi.insertcr(orm, session)
                return orm

    async def add_many(
        self,
        objects: list[BaseModel | Base],
    ) -> list[Base | None]:
        """Default Implementation: Try to Insert objects"""

        tasks = [asyncio.create_task(self.add(obj)) for obj in objects]
        return await asyncio.gather(*tasks)

    async def add_batch(
        self,
        objects: list[BaseModel | Base],
        refresh: bool = False,
    ) -> None:
        """Default Implementation: Batch Insertion"""

        orms = objects
        if isinstance(objects[0], BaseModel):
            orms = [self.ORM.from_pydantic(obj) for obj in objects]

        async with self.dbapi.session() as session:
            await self.dbapi.insertb_r(orms, session)
            if refresh:
                tasks = [asyncio.create_task(session.refresh(orm)) for orm in orms]
                await asyncio.gather(*tasks)

        return orms

    async def goc_batch(
        self,
        objects: list[BaseModel | Base],
        filter_field: InstrumentedAttribute | None = None,
        filter_keys: list[Any] | None = None,
    ) -> list[Base] | None:
        orms = objects
        if isinstance(objects[0], BaseModel):
            orms = [self.ORM.from_pydantic(obj) for obj in objects]

        async with self.dbapi.session() as session:
            orms = await self.dbapi.gocb_r(
                orms,
                session,
                filter_field,
                filter_keys,
            )
            return orms
