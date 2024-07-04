import sys
import asyncio
from pathlib import Path
from functools import wraps
from collections import namedtuple
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from backend.settings import settings
from database.manager import AbstractPersonDataSource
from movies.source import MovieDataSource, TMDbMovieSourceDM
from persons.source import PersonDataSource
from services.tmdb.scraper import TMDbScraper, MovieDoesNotExist
from movies.manager.tmdb_production import TMDbProductionManager
from movies.manager.imdb_movie import IMDbMovieManager
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
from database.manager import (
    DataBaseManagerOnInit,
    AbstractMovieDataSource,
    ExceptionToHandle,
)


class TMDbMovieManager(DataBaseManagerOnInit):
    ORM = TMDbMovieORM

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

        self.production_manager = TMDbProductionManager(
            movie_source,
            exceptions_to_handle,
        )

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.genres = {
                g.tmdb_name: g for g in await self.dbapi.mget(GenreORM, session)
            }

            self.countries = {
                c.iso: c for c in await self.dbapi.mget(CountryORM, session)
            }

        await self.production_manager._initialize()
        self.initialized = True

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.genres:
                del self.genres
            if self.countries:
                del self.countries

            self.production_manager._deinitialize()
            self.initialized = False

    async def get_unprocessed_movies(self) -> list[IMDbMovieORM]:
        async with self.dbapi.session as session:
            return await self.dbapi.mget(
                IMDbMovieORM,
                session,
                IMDbMovieORM.imdb_mvid,
                tmdb_added=False,
            )

    async def add_tmdb_genres(
        self,
        movie_sdm: TMDbMovieSourceDM,
        imdb_id: int,
        session: AsyncSession,
    ) -> None:
        if not movie_sdm.genres:
            return None

        genres = [
            self.genres.get(genre_sdm.tmdb_name, None)
            for genre_sdm in movie_sdm.genres
            if self.genres.get(genre_sdm.tmdb_name, None) is not None
        ]
        movie_genres = [{"imdb_movie_id": imdb_id, "genre_id": g.id} for g in genres]
        await self.dbapi.badd(
            MovieGenreORM,
            session,
            _safe_add=True,
            data=movie_genres,
        )

    async def add_movie_countries(
        self,
        movie_sdm: TMDbMovieSourceDM,
        imdb_id: int,
        tmdb_id: int,
        session: AsyncSession,
    ) -> None:
        if not movie_sdm.countries:
            return

        countries = [
            self.countries[country_sdm.iso] for country_sdm in movie_sdm.countries
        ]
        movie_countries = [
            {
                "country": c.id,
                "imdb_movie": imdb_id,
                "tmdb_movie": tmdb_id,
            }
            for c in countries
        ]
        await self.dbapi.badd(
            MovieCountryORM,
            session,
            _safe_add=True,
            data=movie_countries,
        )

    async def add_movie_productions(
        self,
        productions: ProductionCompanyORM,
        imdb_id: int,
        tmdb_id: int,
        session: AsyncSession,
    ) -> None:
        productions_data = [
            {"production_company": p.id, "imdb_movie": imdb_id, "tmdb_movie": tmdb_id}
            for p in productions
            if p is not None
        ]
        await self.dbapi.badd(
            MovieProductionORM,
            session,
            _safe_add=True,
            data=productions_data,
        )

    async def add_collection(
        self,
        movie_sdm: TMDbMovieSourceDM,
        session: AsyncSession,
    ) -> int | None:
        if not movie_sdm.collection:
            return None

        collection = await self.dbapi.goc(
            MovieCollectionORM,
            session,
            **movie_sdm.collection.to_db(),
        )
        return collection.id if collection else None

    async def mark_up(self, imdb_mvid: str, session: AsyncSession) -> None:
        await self.dbapi.update(
            IMDbMovieORM,
            session,
            filters={"imdb_mvid": imdb_mvid},
            tmdb_added=True,
        )

    async def add(self, movie_sdm: TMDbMovieSourceDM) -> None:
        self.check_initilization()

        async with self.semaphore:
            async with self.dbapi.session as session:
                imdb = await self.dbapi.get(
                    IMDbMovieORM,
                    session,
                    IMDbMovieORM.id,
                    imdb_mvid=movie_sdm.imdb_mvid,
                )

                imdb_id = imdb.id if imdb else None
                if imdb_id is None:
                    return

                collection_id = await self.add_collection(movie_sdm, session)

                tmdb_id = await self.dbapi.add(
                    TMDbMovieORM,
                    session,
                    imdb_movie=imdb_id,
                    movie_collection=collection_id,
                    **movie_sdm.to_db(),
                )
                if not tmdb_id:
                    return

                await self.add_tmdb_genres(movie_sdm, imdb_id, session)
                await self.add_movie_countries(movie_sdm, imdb_id, tmdb_id, session)
                await self.mark_up(movie_sdm.imdb_mvid, session)

                if movie_sdm.productions:
                    productions: list[ProductionCompanyORM] = []
                    for production in movie_sdm.productions:
                        data = await self.production_manager.goc(production, session)
                        if data:
                            productions.append(data)

                    await self.add_movie_productions(
                        productions,
                        imdb_id,
                        tmdb_id,
                        session,
                    )


async def tmdb_movies_init():
    manager = TMDbMovieManager(MovieDataSource())
    imdb_movies = await manager.get_unprocessed_movies()

    tasks = [
        asyncio.create_task(manager.movie_source.get_tmdb_movie(imdb_movie.imdb_mvid))
        for imdb_movie in imdb_movies
    ]
    movies = await tqdm_asyncio.gather(*tasks)
    movies = [m for m in movies if m is not None]

    async with manager as imanager:
        tasks = [asyncio.create_task(imanager.add(movie)) for movie in movies]
        await tqdm_asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(tmdb_movies_init())
