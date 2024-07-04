import sys
import asyncio
from pathlib import Path
from functools import wraps
from collections import namedtuple
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from collections import Counter

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from persons.source import PersonDataSource
from movies.source import ProductionSourceDM, MovieDataSource
from database.manager import (
    DataBaseManagerOnInit,
    AbstractMovieDataSource,
    ExceptionToHandle,
    AbstractPersonDataSource,
)
from database.manager import DataBaseManagerOnInit, ExceptionToHandle
from movies.orm import (
    IMDbMovieORM,
    TMDbMovieORM,
    MovieCollectionORM,
    CountryORM,
    MovieCountryORM,
    ProductionCompanyORM,
    MovieProductionORM,
    GenreORM,
    MovieGenreORM,
)


class TMDbProductionManager(DataBaseManagerOnInit):
    ORM = ProductionCompanyORM

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

        self.production_manager = None

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.countries = {
                c.iso: c for c in await self.dbapi.mget(CountryORM, session)
            }

            productions = await self.dbapi.mget(
                ProductionCompanyORM,
                session,
                ProductionCompanyORM.slug,
            )
            await self.slugger.setup(set([p.slug for p in productions]))

            self.initialized = True

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.countries:
                del self.countries

            self.slugger.clear()
            self.initialized = False

    async def add(self):
        raise NotImplementedError()

    async def badd(self):
        raise NotImplementedError()

    async def goc(
        self,
        production: ProductionSourceDM,
        session: AsyncSession,
    ) -> int | None:
        country = None
        if production.country:
            country = self.countries.get(production.country.iso, None)
        country_id = country.id if country else country

        init_slug = self.slugger.initiate_slug(production.name_en)
        slug = await self.slugger.create_slug(ProductionCompanyORM, session, init_slug)
        return await self.dbapi.goc(
            ProductionCompanyORM,
            session,
            slug=slug,
            country=country_id,
            **production.to_db(),
        )
