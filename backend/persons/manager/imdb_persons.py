import sys
import asyncio
from functools import wraps
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from database.core import Base
from database.api import ExceptionToHandle
from database.manager import DatabaseManager
from movies.orm import IMDbMovieORM
from movies.manager.imdb_movie import IMDbMovieManager
from persons.orm import IMDbPersonORM, ProfessionORM, PersonProfessionORM
from services.imdb.dataset import IMDbDataSet
from services.models import IMDbPersonSDM


def ensure_initialized(full_init):
    def init_wrapper(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.initialized:
                await self._initialize(full_init)
            return await func(self, *args, **kwargs)

        return wrapper

    return init_wrapper


class IMDbPersonManager(DatabaseManager):
    ORM = IMDbPersonORM

    def __init__(
        self,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(exceptions_to_handle)
        self.initialized = False
        self.current_nmids = set()

    async def _initialize(self, full_init: bool) -> None:
        async with self.dbapi.session as session:
            self.professions = {
                mt.imdb_name.lower(): mt
                for mt in await self.dbapi.get(ProfessionORM, session)
            }

            if full_init:
                imdb_persons = await self.dbapi.get(
                    IMDbPersonORM,
                    session,
                    IMDbPersonORM.imdb_nmid,
                    IMDbPersonORM.slug,
                )

                self.current_nmids = {p.imdb_nmid for p in imdb_persons}
                self.slugger.setup({p.slug for p in imdb_persons})

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.professions:
                del self.professions
            if self.current_nmids:
                del self.current_nmids

            self.slugger.clear()

    def create_orm_instance(
        self,
        person: IMDbPersonSDM,
        slug: str,
    ) -> IMDbPersonORM:
        return IMDbPersonORM(
            imdb_nmid=person.imdb_nmid,
            name_en=person.name_en,
            slug=slug,
            birth_y=person.birth_y,
            death_y=person.death_y,
        )

    async def add_professions(
        self,
        person_sdm: IMDbPersonSDM,
        person_orm: IMDbPersonORM,
    ) -> None:
        if person_sdm.professions is None:
            return None
        if len(person_sdm.professions) == 0:
            return None

        profession_orms = [
            self.professions.get(pfn, None) for pfn in person_sdm.professions
        ]

        objects = [
            PersonProfessionORM(
                profession=profession_orm.id,
                person=person_orm.id,
            )
            for profession_orm in profession_orms
            if profession_orm is not None
        ]

        async with self.dbapi.session as session:
            await self.dbapi.gocb_r(objects, session)

    @ensure_initialized(full_init=False)
    async def add(
        self,
        person: IMDbPersonSDM,
        deinitizalize: bool = True,
    ) -> Base | None:
        try:
            async with self.dbapi.session as session:
                init_slug = self.slugger.initiate_slug(person.name_en)
                slug = await self.slugger.create_slug(init_slug, IMDbPersonORM, session)

                person_orm = self.create_orm_instance(person, slug)
                await self.dbapi.insertcr(person_orm, session)

            await self.add_professions(person, person_orm)

            return person_orm

        finally:
            if deinitizalize:
                self._deinitialize()

    @ensure_initialized(full_init=True)
    async def add_many(
        self,
        persons: list[Base | BaseModel],
    ) -> list[Base] | None:
        try:
            tasks = [self.add(p) for p in persons]
            orms = await asyncio.gather(*tasks)
            return orms

        finally:
            self._deinitialize()


async def imdb_persons_init():
    dataset = IMDbDataSet()
    imdbMM = IMDbMovieManager()

    imdb_mvids = await imdbMM.get(IMDbMovieORM.imdb_mvid)
    _, persons = dataset.get_movie_crew(imdb_mvids=[m.imdb_mvid for m in imdb_mvids])

    manager = IMDbPersonManager()
    await manager.add_many(persons)


if __name__ == "__main__":
    asyncio.run(imdb_persons_init())
