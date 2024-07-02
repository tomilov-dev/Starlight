import sys
import asyncio
from pathlib import Path
from functools import wraps
from typing import Any
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

from database.manager import DatabaseManager, ExceptionToHandle
from movies.orm import IMDbMovieORM, MovieTypeORM, GenreORM, MovieGenreORM, Base
from backend.settings import settings
from services.imdb.dataset import IMDbDataSet
from services.models import IMDbMovieSDM
from services.imdb.scraper import IMDbScraper
from manager.genre import GenreManager
from manager.country import CountryManager
from manager.movie_type import MovieTypeManager


def ensure_initialized(full_init):
    def init_wrapper(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.initialized:
                await self._initialize(full_init)
            return await func(self, *args, **kwargs)

        return wrapper

    return init_wrapper


SCRAPER = IMDbScraper(max_rate=5, rate_period=1)


class IMDbMovieManager(DatabaseManager):
    ORM = IMDbMovieORM

    def __init__(
        self,
        exceptions_to_handle: list[ExceptionToHandle] = [
            ExceptionToHandle(IntegrityError, "duplicate key value"),
        ],
    ) -> None:
        super().__init__(exceptions_to_handle)

        self.initialized = False

    async def _initialize(
        self,
        full_init: bool,
    ) -> None:
        async with self.dbapi.session() as session:
            self.movie_types = {
                mt.name_en.lower(): mt
                for mt in await self.dbapi.get(MovieTypeORM, session)
            }
            self.genres = {
                g.name_en: g for g in await self.dbapi.get(GenreORM, session)
            }

            self.created_imdbs = set()
            if full_init:
                current_imdbs = await self.dbapi.get(
                    IMDbMovieORM,
                    session,
                    IMDbMovieORM.imdb_mvid,
                    IMDbMovieORM.slug,
                )
                self.created_imdbs = {ci.imdb_mvid for ci in current_imdbs}
                await self.slugger.setup({ci.slug for ci in current_imdbs})

            self.initialized = True

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.movie_types:
                del self.movie_types
            if self.genres:
                del self.genres
            if self.created_imdbs:
                del self.created_imdbs

            self.slugger.clear()
            self.initialized = False

    def create_orm_instance(
        self,
        movie_sdm: IMDbMovieSDM,
        movie_type: MovieTypeORM,
        slug: str,
    ) -> IMDbMovieORM:
        return IMDbMovieORM(
            imdb_mvid=movie_sdm.imdb_mvid,
            movie_type=movie_type.id,
            name_en=movie_sdm.name_en,
            name_ru=movie_sdm.name_ru,
            slug=slug,
            is_adult=movie_sdm.is_adult,
            runtime=movie_sdm.runtime,
            rate=movie_sdm.rate,
            wrate=movie_sdm.wrate,
            votes=movie_sdm.votes,
            start_year=movie_sdm.start_year,
            end_year=movie_sdm.end_year,
        )

    async def add_imdb_genres(
        self,
        movie_sdm: IMDbMovieSDM,
        imdb: IMDbMovieORM,
        sess: AsyncSession | None = None,
    ) -> None:
        data = [
            MovieGenreORM(
                imdb_movie_id=imdb.id,
                genre_id=self.genres[gn].id,
            )
            for gn in movie_sdm.genres
        ]

        async with self.dbapi.session(sess) as session:
            await self.dbapi.gocb_r(data, session)

    @ensure_initialized(full_init=False)
    async def add(
        self,
        movie_sdm: IMDbMovieSDM,
        deinitialize: bool = True,
        sess: AsyncSession | None = None,
    ) -> IMDbMovieORM | None:
        try:
            movie_type: MovieTypeORM = self.movie_types[movie_sdm.type]
            init_slug = self.slugger.initiate_slug(movie_sdm.name_en)

            movie_sdm.set_init_slug(init_slug)
            async with self.dbapi.session(sess) as session:
                slug = await self.slugger.create_slug(init_slug, IMDbMovieORM, session)

                imdb = self.create_orm_instance(movie_sdm, movie_type, slug)
                await self.dbapi.insertcr(imdb, session)
                await self.add_imdb_genres(movie_sdm, imdb, session)

                return imdb

        except IntegrityError as ex:
            print(ex)

        finally:
            if deinitialize:
                self._deinitialize()

    @ensure_initialized(full_init=True)
    async def add_many(
        self,
        movie_sdms: list[IMDbMovieSDM],
    ) -> list[IMDbMovieORM | None]:
        """Default Implementation: Try to Insert objects"""

        try:
            tasks = [
                asyncio.create_task(self.add(movie_sdm, deinitialize=False))
                for movie_sdm in movie_sdms
            ]
            results = await asyncio.gather(*tasks)

            return results

        finally:
            self._deinitialize()

    async def add_batch(self):
        raise NotImplementedError("IMDbMovieManager.add_batch not implemented")

    async def getj(
        self,
        *attributes: list[InstrumentedAttribute],
        sess: AsyncSession | None = None,
        **filters: dict[str, Any],
    ) -> list[Base] | list[tuple[Any]]:
        query = select(IMDbMovieORM)
        if len(attributes) > 0:
            query = select(*attributes)

        query = query.options(joinedload(IMDbMovieORM.type))
        if len(filters) > 0:
            query = query.filter_by(**filters)

        async with self.dbapi.session(sess) as session:
            data = await session.execute(query)
            if len(attributes) == 0:
                data = data.scalars()
            return data.all()


async def imdb_movies_init():
    dataset = IMDbDataSet(debug=True)
    manager = IMDbMovieManager()

    imdb_movies: list[IMDbMovieSDM] = dataset.get_movies(1000)

    await manager.add_many(imdb_movies)


if __name__ == "__main__":
    asyncio.run(imdb_movies_init())
