import sys
import time
import asyncio
import hashlib
from functools import wraps
from abc import ABC, abstractmethod
from typing import Any, Generator
from pathlib import Path
from slugify import slugify
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.search import SearchClient, MovieSearchDM, PersonSearchDM
from database.core import BaseORM, SessionHandler
from database.api import DataBaseAPI, ExceptionHandler, ExceptionToHandle


MAX_BATCH_SIZE = 1000


class SlugCreationError(Exception):
    pass


def generate_short_hash(text: str, length: int) -> str:
    text_value = (text + str(time.time())).encode()
    sha256_hash = hashlib.sha256(text_value).hexdigest()
    return sha256_hash[:length]


class SourceDataModel(BaseModel):
    @property
    def to_exclude(self) -> list[str]:
        return []

    def to_db(self) -> dict:
        return self.model_dump(exclude=self.to_exclude)


class AbstractMovieDataSource(ABC):
    @abstractmethod
    def get_countries(self) -> list[SourceDataModel]:
        pass

    @abstractmethod
    def get_genres(self) -> list[SourceDataModel]:
        pass

    @abstractmethod
    def get_movie_types(self) -> list[SourceDataModel]:
        pass

    @abstractmethod
    async def get_imdb_movies(self, amount: int) -> list[SourceDataModel]:
        pass

    @abstractmethod
    async def get_tmdb_movie(self, imdb_mvid: str) -> SourceDataModel | None:
        pass

    @abstractmethod
    async def get_imdb_movie_extra(self, imdb_mvid: str) -> SourceDataModel | None:
        pass


class AbstractPersonDataSource(ABC):
    @abstractmethod
    def get_professions(self) -> list[SourceDataModel]:
        pass

    @abstractmethod
    async def get_imdb_persons(self) -> list[SourceDataModel]:
        pass

    @abstractmethod
    async def get_imdb_principals(self) -> list[SourceDataModel]:
        pass


class Slugger:
    def __init__(
        self,
        manager: "DataBaseManager",
        upload_slugs_from_db: bool = False,
    ) -> None:
        self.manager = manager
        self.upload_slugs_from_db = upload_slugs_from_db

        self.created_slugs = set()

    async def setup(
        self,
        slugs_from_db: list[str] | set[str],
    ) -> None:
        self.created_slugs = set()
        if slugs_from_db:
            self.created_slugs.update(set(slugs_from_db))
        if self.upload_slugs_from_db:
            async with self.manager.dbapi.session as session:
                slugs = await self.manager.dbapi.get(
                    self.manager.ORM,
                    session,
                    self.ORM.slug,
                )
                self.created_slugs.update({s.slug for s in slugs})

    def clear(self) -> None:
        self.created_slugs = set()

    def initiate_slug(self, text: str) -> str:
        init_slug = slugify(text)
        slug = init_slug

        index = 1
        while slug in self.created_slugs:
            slug = init_slug + f"-{index}"
            index += 1

            if index >= 11:
                uniq_value = generate_short_hash(init_slug, 8)
                slug = init_slug + f"-{uniq_value}"

        self.created_slugs.add(slug)
        return slug

    async def create_slug(
        self,
        model: BaseORM,
        session: AsyncSession,
        init_slug: str,
    ) -> str:
        if not hasattr(model, "slug"):
            raise AttributeError("ORM doesn't contain slug field")

        slug = init_slug
        exists = await self.manager.dbapi.exists(model, session, slug=slug)
        if not exists:
            return slug

        created = False
        while not created:
            uniq_value = generate_short_hash(init_slug, 8)
            slug = init_slug + f"-{uniq_value}"

            exists = await self.manager.dbapi.exists(model, session, slug=slug)
            if not exists:
                created = True

        self.created_slugs.add(slug)
        if init_slug in self.created_slugs:
            self.created_slugs.remove(init_slug)
        return slug


class AbstractDataBaseManager:
    ORM: BaseORM = None

    def __init__(self) -> None:
        self.dbapi = DataBaseAPI()

        if self.ORM is None:
            raise AttributeError("You should pass ORM to manager class")

    def batching(
        self,
        array: list[object],
    ) -> Generator[Any, Any, list[object]]:
        """Divide the array in batches"""

        for i in range(0, len(array), MAX_BATCH_SIZE):
            yield array[i : i + MAX_BATCH_SIZE]


class DataBaseManager(AbstractDataBaseManager):
    def __init__(
        self,
        movie_source: AbstractMovieDataSource,
        person_source: AbstractPersonDataSource,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__()

        self.slugger = Slugger(self)
        self.exc_handler = ExceptionHandler(exceptions_to_handle)

        self.movie_source = movie_source
        self.person_source = person_source
        self.search = SearchClient()

    async def add(self, object: SourceDataModel) -> int | None:
        async with self.dbapi.session as session:
            return await self.dbapi.add(
                self.ORM,
                session,
                _safe_add=True,
                **object.to_db(),
            )

    async def badd(
        self,
        objects: list[SourceDataModel],
    ) -> None:
        async with self.dbapi.session as session:
            await self.dbapi.badd(
                self.ORM,
                session,
                _safe_add=True,
                data=[o.to_db() for o in objects],
            )


class DataBaseManagerOnInit(ABC, DataBaseManager):
    def __init__(
        self,
        movie_source: AbstractMovieDataSource,
        person_source: AbstractPersonDataSource,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(
            movie_source=movie_source,
            person_source=person_source,
            exceptions_to_handle=exceptions_to_handle,
        )

        self.initialized = False

    @abstractmethod
    async def _initialize(self):
        pass

    @abstractmethod
    def _deinitialize(self):
        pass

    def check_initilization(self) -> None:
        if not self.initialized:
            raise Exception("Manager should be initialized")

    async def __aenter__(self) -> "DataBaseManagerOnInit":
        if not self.initialized:
            await self._initialize()
            self.initialized = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.initialized:
            self._deinitialize()
        return False
