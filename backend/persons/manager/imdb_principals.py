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

    async def add(self, principal: IMDbPrincipalSourceDM) -> None:
        async with self.dbapi.session as session:
            movie = await self.dbapi.get(
                IMDbMovieORM,
                session,
                IMDbMovieORM.id,
                imdb_mvid=principal.imdb_movie,
            )

            movie_id = movie.id if movie else None
            if movie_id is None:
                return None

            person = await self.dbapi.get(
                IMDbPersonORM,
                session,
                IMDbPersonORM.id,
                imdb_nmid=principal.imdb_person,
            )

            person_id = person.id if person else None
            if person_id is None:
                return None

            category = await self.dbapi.get(
                ProfessionORM,
                session,
                ProfessionORM.id,
                imdb_name=principal.category.imdb_name,
            )

            category_id = category.id if category else None
            if category_id is None:
                return None

            await self.dbapi.add(
                MoviePrincipalORM,
                session,
                _safe_add=True,
                imdb_movie=movie_id,
                imdb_person=person_id,
                category=category_id,
                **principal.to_db(),
            )


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

    await manager.add(principals[0])


if __name__ == "__main__":
    asyncio.run(movie_principals_init())
