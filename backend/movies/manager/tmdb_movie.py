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

from services.models import TMDbMovieSDM, ProductionSDM, CollectionSDM
from database.manager import DatabaseManager, ExceptionToHandle
from services.tmdb.scraper import TMDbScraper, MovieDoesNotExist
from services.tmdb.settings import settings
from movies.manager.tmdb_production import TMDbProductionManager
from movies.manager.imdb_movie import IMDbMovieManager

# from movies.manager.tmdb_collection import TMDbCollectionManager
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


SCRAPER = TMDbScraper(
    settings.TMDB_APIKEY,
    settings.PROXY,
    25,
    1,
)


def ensure_initialized(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.initialized:
            await self._initialize()
        return await func(self, *args, **kwargs)

    return wrapper


class TMDbMovieManager(DatabaseManager):
    ORM = TMDbMovieORM

    def __init__(self) -> None:
        super().__init__()

        self.scraper = SCRAPER
        self.production_manager = TMDbProductionManager()
        self.imdb_manager = IMDbMovieManager()

        self.initialized = False

    async def _initialize(self) -> None:
        async with self.dbapi.session as session:
            self.genres = {
                g.tmdb_name: g for g in await self.dbapi.get(GenreORM, session)
            }

            self.countries = {
                c.iso: c for c in await self.dbapi.get(CountryORM, session)
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
        return await self.imdb_manager.get(
            IMDbMovieORM.imdb_mvid,
            tmdb_added=False,
        )

    def create_orm_instance(
        self,
        movie: TMDbMovieSDM,
        imdb_id: int,
        collection_id: int | None,
    ) -> TMDbMovieORM:
        return TMDbMovieORM(
            tmdb_mvid=movie.tmdb_mvid,
            imdb_movie=imdb_id,
            movie_collection=collection_id,
            release_date=movie.release_date,
            budget=movie.budget,
            revenue=movie.revenue,
            image_url=movie.image_url,
            tagline_en=movie.tagline_en,
            overview_en=movie.overview_en,
            tagline_ru=movie.tagline_ru,
            overview_ru=movie.overview_ru,
            rate=movie.rate,
            votes=movie.votes,
            popularity=movie.popularity,
        )

    async def add_tmdb_genres(
        self,
        movie: TMDbMovieSDM,
        imdb_id: int,
    ) -> None:
        if not movie.genres:
            return None

        genres = [
            self.genres.get(gn, None)
            for gn in movie.genres
            if self.genres.get(gn, None) is not None
        ]
        movie_genres = [
            MovieGenreORM(imdb_movie_id=imdb_id, genre_id=g.id) for g in genres
        ]

        async with self.dbapi.session as session:
            await self.dbapi.gocb_r(movie_genres, session)

    async def add_movie_countries(
        self,
        movie: TMDbMovieSDM,
        imdb_id: int,
        tmdb_id: int,
    ) -> None:
        if not movie.countries:
            return

        countries_iso = movie.countries
        countries = [self.countries[iso] for iso in countries_iso]
        movie_countries = [
            MovieCountryORM(country=c.id, imdb_movie=imdb_id, tmdb_movie=tmdb_id)
            for c in countries
        ]

        async with self.dbapi.session as session:
            await self.dbapi.gocb_r(movie_countries, session)

    async def add_movie_productions(
        self,
        productions: ProductionCompanyORM,
        imdb_id: int,
        tmdb_id: int,
    ) -> None:
        mpcs = [
            MovieProductionORM(
                production_company=p.id, imdb_movie=imdb_id, tmdb_movie=tmdb_id
            )
            for p in productions
            if p is not None
        ]

        async with self.dbapi.session as session:
            await self.dbapi.gocb_r(mpcs, session)

    async def mark_up(self, imdb_mvid: str) -> None:
        async with self.dbapi.session as session:
            await self.dbapi.update(
                IMDbMovieORM,
                session,
                filters={"imdb_mvid": imdb_mvid},
                tmdb_added=True,
            )
            await session.commit()

    async def add_collection(
        self,
        movie_sdm: TMDbMovieSDM,
    ) -> MovieCollectionORM | None:
        if not movie_sdm.collection:
            return None

        async with self.dbapi.session as session:
            collection = MovieCollectionORM.from_pydantic(movie_sdm.collection)
            collection = await self.dbapi.goc_r(collection, session)
            return collection

    @ensure_initialized
    async def add(
        self,
        movie_sdm: TMDbMovieSDM,
        deinitialize: bool = True,
    ) -> None:
        try:
            async with self.dbapi.session as session:
                imdb_ids = await self.imdb_manager.get(
                    IMDbMovieORM.id,
                    imdb_mvid=movie_sdm.imdb_mvid,
                )
                imdb_id = imdb_ids[0].id

            collection = await self.add_collection(movie_sdm)
            collection_id = collection.id if collection else None

            tmdb = self.create_orm_instance(movie_sdm, imdb_id, collection_id)
            async with self.dbapi.session as session:
                await self.dbapi.insertcr(tmdb, session)
                tmdb_id = tmdb.id

            await self.add_tmdb_genres(movie_sdm, imdb_id)
            await self.add_movie_countries(movie_sdm, imdb_id, tmdb_id)

            if movie_sdm.productions:
                tasks = [
                    asyncio.create_task(self.production_manager.goc(p))
                    for p in movie_sdm.productions
                ]
                productions = await asyncio.gather(*tasks)
                await self.add_movie_productions(productions, imdb_id, tmdb_id)

            await self.mark_up(movie_sdm.imdb_mvid)

        except IntegrityError as ex:
            print(ex)

        finally:
            if deinitialize:
                self._deinitialize()

    async def add_many(
        self,
        movie_sdms: list[TMDbMovieSDM],
    ) -> None:
        try:
            tasks = [
                asyncio.create_task(self.add(movie_sdm, False))
                for movie_sdm in movie_sdms
            ]
            return await asyncio.gather(*tasks)

        finally:
            self._deinitialize()


async def get_movie(imdb_movie: IMDbMovieORM) -> TMDbMovieSDM | None:
    try:
        return await SCRAPER.get_movie(imdb_movie.imdb_mvid)
    except MovieDoesNotExist:
        pass


async def tmdb_movies_init():
    manager = TMDbMovieManager()

    imdb_movies = await manager.get_unprocessed_movies()

    tasks = [asyncio.create_task(get_movie(imdb_movie)) for imdb_movie in imdb_movies]
    movies = await tqdm_asyncio.gather(*tasks)
    movies = [m for m in movies if m is not None]

    await manager.add_many(movies)


if __name__ == "__main__":
    asyncio.run(tmdb_movies_init())
