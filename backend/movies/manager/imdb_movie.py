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

from persons.source import PersonDataSource
from movies.source import MovieDataSource
from movies.source import IMDbMovieSourceDM
from movies.orm import IMDbMovieORM, MovieTypeORM, GenreORM, MovieGenreORM, BaseORM
from backend.settings import settings
from services.imdb.dataset import IMDbDataSet
from services.imdb.scraper import IMDbScraper
from movies.manager.genre import GenreManager
from movies.manager.country import CountryManager
from movies.manager.movie_type import MovieTypeManager
from database.manager import (
    DataBaseManagerOnInit,
    ExceptionToHandle,
    AbstractMovieDataSource,
    AbstractPersonDataSource,
)


class IMDbMovieManager(DataBaseManagerOnInit):
    ORM = IMDbMovieORM

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

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.movie_types = {
                mt.name_en.lower(): mt
                for mt in await self.dbapi.mget(MovieTypeORM, session)
            }
            self.genres = {
                g.name_en: g for g in await self.dbapi.mget(GenreORM, session)
            }

            self.created_imdbs = set()
            await self.slugger.setup([])
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

    async def add_imdb_genres(
        self,
        movie_sdm: IMDbMovieSourceDM,
        imdb_id: int,
        session: AsyncSession | None = None,
    ) -> None:
        movie_genres = []
        for genre_sdm in movie_sdm.genres:
            genre_orm = self.genres.get(genre_sdm.name_en)
            genre_id = genre_orm.id if genre_orm else None
            if genre_id:
                movie_genres.append({"imdb_movie_id": imdb_id, "genre_id": genre_id})

        if movie_genres:
            await self.dbapi.badd(
                MovieGenreORM,
                session,
                _safe_add=True,
                data=movie_genres,
            )

    async def add(self, movie_sdm: IMDbMovieSourceDM) -> None:
        self.check_initilization()

        async with self.exc_handler:
            async with self.dbapi.session as session:
                movie_type: MovieTypeORM = self.movie_types.get(
                    movie_sdm.movie_type.imdb_name
                )
                init_slug = self.slugger.initiate_slug(movie_sdm.name_en)

                slug = await self.slugger.create_slug(IMDbMovieORM, session, init_slug)
                imdb_id = await self.dbapi.add(
                    self.ORM,
                    session,
                    movie_type=movie_type.id,
                    slug=slug,
                    **movie_sdm.to_db(),
                )

                if imdb_id:
                    await self.add_imdb_genres(movie_sdm, imdb_id, session)

    async def getj(
        self,
        *attributes: list[InstrumentedAttribute],
        sess: AsyncSession | None = None,
        **filters: dict[str, Any],
    ) -> list[BaseORM] | list[tuple[Any]]:
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
    manager = IMDbMovieManager(MovieDataSource())
    imdb_movies = await manager.movie_source.get_imdb_movies(1000)

    async with manager as imanager:
        tasks = [asyncio.create_task(imanager.add(m)) for m in imdb_movies]
        await tqdm_asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(imdb_movies_init())
