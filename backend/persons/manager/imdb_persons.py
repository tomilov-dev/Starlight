import sys
import asyncio
from typing import Any
from pathlib import Path
from pydantic import BaseModel
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import joinedload
from sqlalchemy import select

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from backend.settings import settings
from database.api import ExceptionToHandle
from database.manager import AbstractMovieDataSource, AbstractPersonDataSource
from database.manager import DataBaseManagerOnInit, PersonSearchDM
from movies.orm import IMDbMovieORM
from persons.orm import BaseORM
from movies.manager.imdb_movie import IMDbMovieManager
from persons.orm import (
    IMDbPersonORM,
    ProfessionORM,
    PersonProfessionORM,
    MoviePrincipalORM,
)
from services.imdb.dataset import IMDbDataSet
from persons.source import PersonDataSource, IMDbPersonSourceDM
from movies.source import MovieDataSource


class IMDbPersonManager(DataBaseManagerOnInit):
    ORM = IMDbPersonORM

    def __init__(
        self,
        movie_source: AbstractMovieDataSource = MovieDataSource(),
        person_source: AbstractPersonDataSource = PersonDataSource(),
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(
            movie_source=movie_source,
            person_source=person_source,
            exceptions_to_handle=exceptions_to_handle,
        )

        semlimit = (settings.PG_POOL_SIZE + settings.PG_MAX_OVERFLOW) // 2
        self.semaphore = asyncio.Semaphore(semlimit)

        self.initialized = False
        self.current_nmids = set()

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.professions = {
                mt.imdb_name.lower(): mt
                for mt in await self.dbapi.mget(ProfessionORM, session)
            }
            await self.slugger.setup([])

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.professions:
                del self.professions
            if self.current_nmids:
                self.current_nmids = set()

            self.slugger.clear()

    async def add_professions(
        self,
        person_sdm: IMDbPersonSourceDM,
        person_id: int,
        session: AsyncSession,
    ) -> None:
        if not person_sdm.professions:
            return None

        professions = [
            self.professions.get(p.imdb_name.lower(), None)
            for p in person_sdm.professions
        ]

        professions = [p for p in professions if p is not None]
        if professions:
            data = [
                {
                    "profession_id": p.id,
                    "person_id": person_id,
                }
                for p in professions
            ]
            await self.dbapi.badd(
                PersonProfessionORM,
                session,
                _safe_add=True,
                data=data,
            )

    async def add(self, person_sdm: IMDbPersonSourceDM) -> int | None:
        async with self.semaphore:

            init_slug = self.slugger.initiate_slug(person_sdm.name_en)
            async with self.dbapi.session as session:
                slug = await self.slugger.create_slug(
                    IMDbPersonORM,
                    session,
                    init_slug,
                )

                person_id = await self.dbapi.add(
                    IMDbPersonORM,
                    session,
                    _safe_add=True,
                    slug=slug,
                    **person_sdm.to_db(),
                )

                if person_id:
                    await self.search.add_person(
                        PersonSearchDM(
                            id=person_id,
                            name_en=person_sdm.name_en,
                        )
                    )
                    await self.add_professions(person_sdm, person_id, session)

    async def get_persons(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> list[IMDbPersonORM]:
        query = select(IMDbPersonORM)
        query = query.limit(page_size).offset((page - 1) * page_size)

        async with self.dbapi.session as session:
            persons = await session.execute(query)
            return persons.scalars().all()

    async def search_persons(self, text_query: str) -> list[IMDbPersonORM]:
        searched_persons = await self.search.get_persons(text_query)
        persons_ids = [p.id for p in searched_persons]

        query = select(IMDbPersonORM)
        query = query.where(IMDbPersonORM.id.in_(persons_ids))
        async with self.dbapi.session as session:
            persons = await session.execute(query)
            return persons.scalars().all()

    async def get_person(self, slug: str) -> IMDbPersonORM:
        query = select(IMDbPersonORM)
        query = query.options(joinedload(IMDbPersonORM.tmdb))
        query = query.options(
            joinedload(IMDbPersonORM.professions).options(
                joinedload(PersonProfessionORM.profession)
            )
        )
        query = query.options(
            joinedload(IMDbPersonORM.movies).options(
                joinedload(MoviePrincipalORM.imdb_movie).options(
                    joinedload(IMDbMovieORM.type)
                )
            )
        )
        query = query.where(IMDbPersonORM.slug == slug)

        async with self.dbapi.session as session:
            person = await session.execute(query)
            return person.scalars().first()


async def imdb_persons_init():
    manager = IMDbPersonManager()
    person_ds = PersonDataSource()

    imdbs: list[IMDbMovieORM] = []
    async with manager.dbapi.session as session:
        imdbs = await manager.dbapi.mget(
            IMDbMovieORM,
            session,
            IMDbMovieORM.id,
            IMDbMovieORM.imdb_mvid,
            principals_added=False,
        )

    persons = await person_ds.get_imdb_persons([m.imdb_mvid for m in imdbs])
    async with manager as imanager:
        async with imanager.search:
            tasks = [asyncio.create_task(imanager.add(p)) for p in persons]
            await tqdm_asyncio.gather(*tasks)


async def reindex_persons():
    manager = IMDbPersonManager()

    async with manager.dbapi.session as session:
        persons = await manager.dbapi.mget(IMDbPersonORM, session)
        data = [PersonSearchDM(id=m.id, name_en=m.name_en) for m in persons]
        await manager.search.add_persons(data)


if __name__ == "__main__":
    asyncio.run(imdb_persons_init())
