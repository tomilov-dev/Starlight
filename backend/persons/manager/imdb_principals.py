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
from persons.orm import MoviePrincipalORM, IMDbPersonORM
from services.imdb.dataset import IMDbDataSet
from services.models import IMDbPrincipalSDM


class IMDbMoviePrincipalManager(DatabaseManager):
    ORM = MoviePrincipalORM

    def create_orm_instance(
        self,
        principal: IMDbPrincipalSDM,
        movie_id: int,
        person_id: int,
    ) -> MoviePrincipalORM:
        return MoviePrincipalORM(
            imdb_movie=movie_id,
            imdb_person=person_id,
            category=ValueError(),
            ordering=principal.ordering,
            job=principal.job,
            characters=principal.characters,
        )

    async def add(
        self,
        principal: IMDbPrincipalSDM,
    ) -> MoviePrincipalORM | None:
        async with self.dbapi.session as session:
            movie_id = await self.dbapi.get(
                IMDbMovieORM,
                session,
                IMDbMovieORM.id,
                imdb_mvid=principal.imdb_movie,
            )

            if movie_id is None:
                return None

            person_id = await self.dbapi.get(
                IMDbPersonORM,
                session,
                IMDbPersonORM.id,
                imdb_nmid=principal.imdb_person,
            )

            if person_id is None:
                return None


async def movie_principals_init():
    dataset = IMDbDataSet()
    imdbMM = IMDbMovieManager()

    imdb_mvids = await imdbMM.get(IMDbMovieORM.imdb_mvid)
    principals, _ = dataset.get_movie_crew(imdb_mvids=[m.imdb_mvid for m in imdb_mvids])

    manager = IMDbMoviePrincipalManager()
    manager.add(principals[0])


if __name__ == "__main__":
    asyncio.run(movie_principals_init())
