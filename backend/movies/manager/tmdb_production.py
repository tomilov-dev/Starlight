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

from services.models import ProductionSDM
from database.manager import DatabaseManager, ExceptionToHandle
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


class TMDbProductionManager(DatabaseManager):
    ORM = ProductionCompanyORM

    def __init__(self) -> None:
        super().__init__()

        self.initialized = False

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.countries = {
                c.iso: c for c in await self.dbapi.get(CountryORM, session)
            }

            productions = await self.dbapi.get(
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

    def create_orm_instance(
        self,
        production: ProductionSDM,
        country: int,
        slug: str,
    ) -> ProductionCompanyORM:
        return ProductionCompanyORM(
            tmdb_id=production.tmdb_id,
            country=country,
            name_en=production.name_en,
            slug=slug,
            image_url=production.image_url,
        )

    async def goc(
        self,
        production: ProductionSDM,
        **filters,
    ) -> ProductionCompanyORM | None:
        async with self.dbapi.session as session:
            exists = await self.dbapi.exists(
                ProductionCompanyORM,
                session,
                tmdb_id=production.tmdb_id,
                **filters,
            )

            if exists:
                orms = await self.dbapi.get(
                    ProductionCompanyORM,
                    session,
                    tmdb_id=production.tmdb_id,
                    **filters,
                )
                orm = orms[0]
                return orm

        return await self.add(production)

    async def add(self, production: ProductionSDM) -> ProductionCompanyORM | None:
        country = self.countries.get(production.country, None)
        country = country.id if country else country

        init_slug = self.slugger.initiate_slug(production.name_en)
        production.set_init_slug(init_slug)

        async with self.dbapi.session as session:
            slug = await self.slugger.create_slug(
                init_slug,
                ProductionCompanyORM,
                session,
            )

            production_orm = self.create_orm_instance(production, country, slug)
            production_orm = await self.dbapi.goc_r(production_orm, session)

            return production_orm
