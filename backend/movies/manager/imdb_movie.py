import sys
import asyncio
from enum import Enum
from pathlib import Path
from functools import wraps
from typing import Any
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import joinedload
from sqlalchemy import select, Select, func

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from persons.source import PersonDataSource
from movies.source import MovieDataSource
from movies.source import IMDbMovieSourceDM
from persons.orm import IMDbPersonORM, MoviePrincipalORM
from movies.orm import (
    IMDbMovieORM,
    ContentTypeORM,
    GenreORM,
    MovieGenreORM,
    BaseORM,
    TMDbMovieORM,
    MovieCountryORM,
    CountryORM,
    ProductionCompanyORM,
    MovieProductionORM,
)
from database.manager import (
    DataBaseManagerOnInit,
    ExceptionToHandle,
    AbstractMovieDataSource,
    AbstractPersonDataSource,
    MovieSearchDM,
)
from users.orm import UserMovieScoreORM, UserORM


class MoviesOrderBy(Enum):
    YEAR = "year"  # year
    RATE = "rate"  # IMDb rate
    WRATE = "wrate"  # Weighted rate
    VOTES = "votes"  # Votes count

    DEFAULT = "year"


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
            self.content_types = {
                mt.name_en.lower(): mt
                for mt in await self.dbapi.mget(ContentTypeORM, session)
            }
            self.genres = {
                g.name_en: g for g in await self.dbapi.mget(GenreORM, session)
            }

            self.created_imdbs = set()
            await self.slugger.setup([])
            self.initialized = True

    def _deinitialize(self) -> None:
        if self.initialized:
            if self.content_types:
                del self.content_types
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
                content_type: ContentTypeORM = self.content_types.get(
                    movie_sdm.content_type.imdb_name
                )
                init_slug = self.slugger.initiate_slug(movie_sdm.name_en)

                slug = await self.slugger.create_slug(IMDbMovieORM, session, init_slug)
                imdb_id = await self.dbapi.add(
                    self.ORM,
                    session,
                    content_type=content_type.id,
                    slug=slug,
                    **movie_sdm.to_db(),
                )

                if imdb_id:
                    await self.search.add_movie(
                        MovieSearchDM(
                            id=imdb_id,
                            name_en=movie_sdm.name_en,
                            name_ru=movie_sdm.name_ru,
                        )
                    )
                    await self.add_imdb_genres(movie_sdm, imdb_id, session)

    async def get(
        self,
        *attributes: list[InstrumentedAttribute],
        **filters: dict[str, Any],
    ) -> list[BaseORM] | list[tuple[Any]]:
        qmovie = select(*attributes) if attributes else select(IMDbMovieORM)
        qmovie = qmovie.options(joinedload(IMDbMovieORM.type))
        qmovie = qmovie.options(
            joinedload(IMDbMovieORM.tmdb).joinedload(TMDbMovieORM.collection)
        )
        qmovie = qmovie.filter_by(**filters) if filters else qmovie

        async with self.dbapi.session as session:
            movie = await session.execute(qmovie)
            if attributes:
                return movie.all()

            return movie.scalars().all()

    async def get_extended_movie_data(self, slug: str) -> IMDbMovieORM:
        query = select(IMDbMovieORM)
        query = query.options(joinedload(IMDbMovieORM.type))
        query = query.options(
            joinedload(IMDbMovieORM.tmdb).joinedload(TMDbMovieORM.collection)
        )
        query = query.options(
            joinedload(IMDbMovieORM.genres).joinedload(MovieGenreORM.genre)
        )
        query = query.options(
            joinedload(IMDbMovieORM.countries).joinedload(MovieCountryORM.country)
        )
        query = query.options(
            joinedload(IMDbMovieORM.production_companies)
            .joinedload(MovieProductionORM.production_company)
            .joinedload(ProductionCompanyORM.country_origin)
        )
        query = query.options(
            joinedload(IMDbMovieORM.principals).options(
                joinedload(MoviePrincipalORM.imdb_person)
            )
        )
        query = query.where(IMDbMovieORM.slug == slug)

        async with self.dbapi.session as session:
            movie = await session.execute(query)
            return movie.scalars().first()

    async def search_movies(self, text_query: str) -> list[IMDbMovieORM]:
        searched_movies = await self.search.get_movies(text_query)
        movies_ids = [m.id for m in searched_movies]

        query = select(IMDbMovieORM).options(joinedload(IMDbMovieORM.type))
        query = query.where(IMDbMovieORM.id.in_(movies_ids))
        async with self.dbapi.session as session:
            movies = await session.execute(query)
            return movies.scalars().all()

    def add_pagination(
        self,
        query: Select,
        page: int,
        page_size: int,
    ) -> Select:
        return query.limit(page_size).offset((page - 1) * page_size)

    def add_filters(
        self,
        query: Select,
        start_year: int | None,
        end_year: int | None,
        rate: float | None,
        wrate: float | None,
        votes: int | None,
        adult: bool | None,
    ):
        if start_year is not None:
            query = query.where(IMDbMovieORM.start_year >= start_year)
        if end_year is not None:
            query = query.where(IMDbMovieORM.start_year <= end_year)
        if rate is not None:
            query = query.where(IMDbMovieORM.rate >= rate)
        if wrate is not None:
            query = query.where(IMDbMovieORM.wrate >= wrate)
        if votes is not None:
            query = query.where(IMDbMovieORM.votes >= votes)
        if adult is not None:
            query = query.where(IMDbMovieORM.is_adult == adult)

        return query

    def exclude_watched_by_user(
        self,
        query: Select,
        user_id: int | None,
    ) -> Select:
        if user_id is not None:
            subquery = select(UserMovieScoreORM.movie_id)
            query = query.where(IMDbMovieORM.id.notin_(subquery))
        return query

    def add_in_subqueries(
        self,
        query: Select,
        include_genre: list[int] | None,
        exclude_genre: list[int] | None,
        include_country: list[int] | None,
        exclude_country: list[int] | None,
    ):
        if include_genre:
            subquery = (
                select(IMDbMovieORM.id)
                .join(
                    MovieGenreORM,
                    IMDbMovieORM.id == MovieGenreORM.imdb_movie_id,
                )
                .filter(MovieGenreORM.genre_id.in_(include_genre))
                .group_by(IMDbMovieORM.id)
                .having(func.count(MovieGenreORM.genre_id) == len(include_genre))
            )
            query = query.where(IMDbMovieORM.id.in_(subquery))

        if exclude_genre:
            subquery = (
                select(IMDbMovieORM.id)
                .join(
                    MovieGenreORM,
                    IMDbMovieORM.id == MovieGenreORM.imdb_movie_id,
                )
                .filter(MovieGenreORM.genre_id.in_(exclude_genre))
            )
            query = query.where(~IMDbMovieORM.id.in_(subquery))

        if include_country:
            subquery = (
                select(IMDbMovieORM.id)
                .join(
                    MovieCountryORM,
                    IMDbMovieORM.id == MovieCountryORM.imdb_movie_id,
                )
                .filter(MovieCountryORM.country_id.in_(include_country))
                .group_by(IMDbMovieORM.id)
                .having(func.count(MovieCountryORM.country_id) == len(include_country))
            )
            query = query.where(IMDbMovieORM.id.in_(subquery))

        if exclude_country:
            subquery = (
                select(IMDbMovieORM.id)
                .join(
                    MovieCountryORM,
                    IMDbMovieORM.id == MovieCountryORM.imdb_movie_id,
                )
                .filter(MovieCountryORM.country_id.in_(exclude_country))
            )
            query = query.where(~IMDbMovieORM.id.in_(subquery))

        return query

    def add_order_by(
        self,
        query: Select,
        order_by: MoviesOrderBy,
        ascending: bool,
    ) -> Select:
        if order_by == MoviesOrderBy.YEAR:
            if ascending:
                query = query.order_by(IMDbMovieORM.start_year.asc())
            else:
                query = query.order_by(IMDbMovieORM.start_year.desc())
        elif order_by == MoviesOrderBy.RATE:
            if ascending:
                query = query.order_by(IMDbMovieORM.rate.asc())
            else:
                query = query.order_by(IMDbMovieORM.rate.desc())
        elif order_by == MoviesOrderBy.WRATE:
            if ascending:
                query = query.order_by(IMDbMovieORM.wrate.asc())
            else:
                query = query.order_by(IMDbMovieORM.wrate.desc())
        elif order_by == MoviesOrderBy.VOTES:
            if ascending:
                query = query.order_by(IMDbMovieORM.votes.asc())
            else:
                query = query.order_by(IMDbMovieORM.votes.desc())

        return query

    async def select_movies(
        self,
        page: int = 1,
        page_size: int = 10,
        include_genre: list[int] | None = None,
        exclude_genre: list[int] | None = None,
        include_country: list[int] | None = None,
        exclude_country: list[int] | None = None,
        order_by: MoviesOrderBy = MoviesOrderBy.DEFAULT,
        ascending: bool = True,
        start_year: int | None = None,
        end_year: int | None = None,
        rate: float | None = None,
        wrate: float | None = None,
        votes: int | None = None,
        adult: bool | None = None,
        user_id: int | None = None,
    ) -> list[IMDbMovieORM]:
        query = select(IMDbMovieORM).distinct()
        query = query.options(joinedload(IMDbMovieORM.type))

        if include_genre or exclude_genre:
            query = query.join(
                MovieGenreORM,
                IMDbMovieORM.id == MovieGenreORM.imdb_movie_id,
            )
        if include_country or exclude_country:
            query = query.join(
                MovieCountryORM,
                IMDbMovieORM.id == MovieCountryORM.imdb_movie_id,
            )

        query = self.add_filters(query, start_year, end_year, rate, wrate, votes, adult)
        query = self.add_in_subqueries(
            query,
            include_genre,
            exclude_genre,
            include_country,
            exclude_country,
        )
        query = self.exclude_watched_by_user(query, user_id)

        query = self.add_order_by(query, order_by, ascending)
        query = self.add_pagination(query, page, page_size)

        async with self.dbapi.session as session:
            result = await session.execute(query)
            movies = result.scalars().all()

        return movies

    async def get_movies_by_genre(
        self,
        genre_slug: str,
        page: int = 1,
        page_size: int = 10,
        order_by: MoviesOrderBy = MoviesOrderBy.DEFAULT,
        ascending: bool = True,
        start_year: int | None = None,
        end_year: int | None = None,
        rate: float | None = None,
        wrate: float | None = None,
        votes: int | None = None,
        adult: bool | None = None,
        user_id: int | None = None,
    ) -> list[IMDbMovieORM]:
        query = select(IMDbMovieORM).distinct()
        query = query.join(
            MovieGenreORM, IMDbMovieORM.id == MovieGenreORM.imdb_movie_id
        )
        query = query.join(GenreORM, GenreORM.id == MovieGenreORM.genre_id)
        query = query.options(joinedload(IMDbMovieORM.type))

        query = self.exclude_watched_by_user(query, user_id)

        query = self.add_filters(query, start_year, end_year, rate, wrate, votes, adult)
        query = self.add_order_by(query, order_by, ascending)

        query = query.where(GenreORM.slug == genre_slug)
        query = self.add_pagination(query, page, page_size)

        async with self.dbapi.session as session:
            result = await session.execute(query)
            return result.scalars().all()


async def imdb_movies_init():
    manager = IMDbMovieManager()
    imdb_movies = await manager.movie_source.get_imdb_movies(1000)

    async with manager as imanager:
        async with imanager.search:
            tasks = [asyncio.create_task(imanager.add(m)) for m in imdb_movies]
            await tqdm_asyncio.gather(*tasks)


async def reindex_movies():
    manager = IMDbMovieManager()

    async with manager.dbapi.session as session:
        movies = await manager.dbapi.mget(IMDbMovieORM, session)
        data = [
            MovieSearchDM(id=m.id, name_en=m.name_en, name_ru=m.name_ru) for m in movies
        ]
        await manager.search.add_movies(data)


if __name__ == "__main__":
    asyncio.run(imdb_movies_init())
