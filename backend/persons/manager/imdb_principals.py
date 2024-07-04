import sys
import asyncio
from functools import wraps
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))
sys.path.append(str(PROJ_DIR.parent))

from backend.settings import settings
from database.api import ExceptionToHandle
from movies.orm import IMDbMovieORM
from movies.manager.imdb_movie import IMDbMovieManager
from persons.orm import MoviePrincipalORM, IMDbPersonORM, ProfessionORM
from services.imdb.dataset import IMDbDataSet
from persons.source import IMDbPrincipalSourceDM, PersonDataSource
from movies.source import MovieDataSource
from database.manager import (
    DataBaseManager,
    AbstractMovieDataSource,
    AbstractPersonDataSource,
)


class IMDbMoviePrincipalManager(DataBaseManager):
    ORM = MoviePrincipalORM

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

    async def get_movie_id(
        self,
        principal: IMDbPrincipalSourceDM,
        session: AsyncSession,
    ) -> int | None:
        imdb_movie = await self.dbapi.get(
            IMDbMovieORM,
            session,
            IMDbMovieORM.id,
            imdb_mvid=principal.imdb_movie,
        )

        imdb_movie_id = imdb_movie.id if imdb_movie else None
        if imdb_movie_id is None:
            return None
        return imdb_movie_id

    async def get_person_id(
        self,
        principal: IMDbPrincipalSourceDM,
        session: AsyncSession,
    ) -> int | None:
        imdb_person = await self.dbapi.get(
            IMDbPersonORM,
            session,
            IMDbPersonORM.id,
            imdb_nmid=principal.imdb_person,
        )

        imdb_person_id = imdb_person.id if imdb_person else None
        if imdb_person_id is None:
            return None
        return imdb_person_id

    async def get_category_id(
        self,
        principal: IMDbPrincipalSourceDM,
        session: AsyncSession,
    ) -> int | None:
        category = await self.dbapi.get(
            ProfessionORM,
            session,
            ProfessionORM.id,
            imdb_name=principal.category.imdb_name,
        )

        category_id = category.id if category else None
        if category_id is None:
            return None
        return category_id

    async def mark_up(
        self,
        imdb_id: int,
        session: AsyncSession,
    ) -> None:
        await self.dbapi.update(
            IMDbMovieORM,
            session,
            filters={"id": imdb_id},
            principals_added=True,
        )

    async def add(self, principal: IMDbPrincipalSourceDM) -> None:
        async with self.semaphore:
            async with self.dbapi.session as session:
                movie_id = await self.get_movie_id(principal, session)
                if not movie_id:
                    return

                person_id = await self.get_person_id(principal, session)
                if not person_id:
                    return

                category_id = await self.get_category_id(principal, session)
                if not category_id:
                    return

                await self.dbapi.add(
                    MoviePrincipalORM,
                    session,
                    _safe_add=True,
                    imdb_movie=movie_id,
                    imdb_person=person_id,
                    category=category_id,
                    **principal.to_db(),
                )
                await self.mark_up(movie_id, session)


async def movie_principals_init():
    manager = IMDbMoviePrincipalManager()

    imdbs: list[IMDbMovieORM] = []
    async with manager.dbapi.session as session:
        imdbs = await manager.dbapi.mget(
            IMDbMovieORM,
            session,
            IMDbMovieORM.id,
            IMDbMovieORM.imdb_mvid,
            principals_added=False,
        )

    principals = await manager.person_source.get_imdb_principals(
        imdb_mvids=[m.imdb_mvid for m in imdbs]
    )

    tasks = [asyncio.create_task(manager.add(p)) for p in principals]
    await tqdm_asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(movie_principals_init())
