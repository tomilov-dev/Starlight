import sys
import asyncio
from pathlib import Path
from collections import namedtuple
from tqdm.asyncio import tqdm_asyncio
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from collections import Counter

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from services.tmdb.scraper import TMDbScraper, TMDbMovie, Production, MovieDoesNotExist
from services.tmdb.settings import settings
from database.core import SlugCreationError
from movies.orm import (
    IMDbORM,
    TMDbORM,
    CollectionORM,
    CountryORM,
    MovieCountryORM,
    ProductionCompanyORM,
    MovieProductionORM,
    GenreORM,
)


SCRAPER = TMDbScraper(
    settings.APIKEY,
    settings.TEST_PROXY,
    25,
    1,
)


class ProductionData:
    def __init__(
        self,
        imdb_id: int,
        tmdb_id: int,
        movie: TMDbMovie,
    ):
        self.imdb_id = imdb_id
        self.tmdb_id = tmdb_id
        self.movie = movie


class MovieProductionData:
    def __init__(
        self,
        imdb_id: int,
        tmdb_id: int,
        production_name: str,
    ):
        self.imdb_id = imdb_id
        self.tmdb_id = tmdb_id
        self.production_name = production_name

    def __hash__(self) -> str:
        return hash((self.imdb_id, self.tmdb_id, self.production_name))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MovieProductionData):
            return False
        return (
            self.imdb_id == other.imdb_id
            and self.tmdb_id == other.tmdb_id
            and self.production_name == other.production_name
        )

    def __repr__(self) -> str:
        return f"{self.imdb_id} :: {self.production_name}"


class TMDbMovieAdder(DatabaseAdder):
    def __init__(self) -> None:
        super().__init__()

        self.scraper = SCRAPER

    async def mark_up(
        self,
        imdb_mvid: str,
    ) -> None:
        async with self.mvdb.session as session:
            await self.mvdb.update(
                IMDbORM,
                session,
                filters={"imdb_mvid": imdb_mvid},
                tmdb_added=True,
            )
            await session.commit()

    async def add_production(
        self,
        production: Production,
    ) -> ProductionCompanyORM:
        try:
            country = self.countries.get(production.country, None)
            country = country.id if country else country

            init_slug = self.mvdb.initiate_slug(
                production.name,
                self.created_production_slugs,
            )

            async with self.mvdb.session as session:
                slug = await self.mvdb.create_slug(
                    init_slug,
                    ProductionCompanyORM,
                    session,
                )

                production_orm = ProductionCompanyORM(
                    country=country,
                    name_en=production.name,
                    slug=slug,
                    image_url=production.image_url,
                )
                production_orm = await self.mvdb.goc(
                    production_orm,
                    ProductionCompanyORM,
                    session,
                    name_en=production_orm.name_en,
                )
                return production_orm

        except SlugCreationError as ex:
            print(ex)

    async def add_production_companies(
        self,
        production_companies: list[Production],
    ) -> list[ProductionCompanyORM]:
        tasks = [self.add_production(pc) for pc in production_companies]

        print("Insert Production Companies")
        productions: list[ProductionCompanyORM] = await tqdm_asyncio.gather(*tasks)

        return productions

    async def add_movie_production(
        self,
        movie_production: MovieProductionORM,
    ) -> None:
        async with self.mvdb.session as session:
            await self.mvdb.insert(movie_production, session)
            await session.commit()

    async def add_movie_productions(
        self,
        movie_productions_data: list[MovieProductionData],
    ):
        movie_productions = []
        for mpd in movie_productions_data:
            pc: ProductionCompanyORM = self.productions.get(mpd.production_name, None)
            if pc:
                mp = MovieProductionORM(
                    production_company=pc.id,
                    imdb_movie=mpd.imdb_id,
                    tmdb_movie=mpd.tmdb_id,
                )
                movie_productions.append(mp)

        tasks = [self.add_movie_production(mp) for mp in movie_productions]

        print("Batch Insert Movie Productions")
        await tqdm_asyncio.gather(*tasks)

    async def process_production_data(
        self,
        production_data: list[ProductionData],
    ) -> None:
        production_companies: set[Production] = set()
        movie_productions_data: set[MovieProductionData] = set()

        for pd in production_data:
            if pd and pd.movie and pd.movie.productions:
                for pc in pd.movie.productions:
                    production_companies.add(pc)

                    mpd = MovieProductionData(pd.imdb_id, pd.tmdb_id, pc.name)
                    movie_productions_data.add(mpd)

        productions = await self.add_production_companies(production_companies)
        self.productions = {p.name_en: p for p in productions if p}

        await self.add_movie_productions(movie_productions_data)

    async def add_movie_countries(
        self,
        imdb_id: int,
        tmdb_id: int,
        movie: TMDbMovie,
    ) -> None:
        if movie.countries:
            countries_iso = movie.countries
            countries = [self.countries[iso] for iso in countries_iso]

            movie_countries = [
                MovieCountryORM(
                    country=c.id,
                    imdb_movie=imdb_id,
                    tmdb_movie=tmdb_id,
                )
                for c in countries
            ]

            async with self.mvdb.session as session:
                await self.mvdb.insertb(movie_countries, session)
                await session.commit()

    async def add_movie_genres(self, movie: TMDbMovie) -> None:
        async with self.mvdb.session as session:
            genres = [self.genres[g] for g in movie.genres]
            for genre in genres:
                try:
                    await self.mvdb.insert(genre, session)

                except IntegrityError as ex:
                    print("Line 123 IntegrityError:", ex)

                except InvalidRequestError as ex:
                    print("Line 123 InvalidRequestError:", ex)

            await session.commit()

    def setup_tmdb(
        self,
        movie: TMDbMovie,
        imdb_id: int,
        collection_id: int | None,
    ) -> TMDbORM:
        return TMDbORM(
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

    async def add(
        self,
        imdb_id: int,
        imdb_mvid: str,
    ) -> ProductionData:
        try:
            movie: TMDbMovie = await self.scraper.get_movie(imdb_mvid)

            async with self.mvdb.session as session:

                collection_id = None
                if movie.collection:
                    collection = CollectionORM(
                        name_en=movie.collection.name_en,
                        name_ru=movie.collection.name_ru,
                    )

                    collection: CollectionORM = await self.mvdb.goc(
                        collection,
                        CollectionORM,
                        session,
                        name_en=collection.name_en,
                    )
                    collection_id = collection.id

                tmdb = self.setup_tmdb(movie, imdb_id, collection_id)
                tmdb: TMDbORM = await self.mvdb.goc(
                    tmdb,
                    TMDbORM,
                    session,
                    tmdb_mvid=tmdb.tmdb_mvid,
                )

                tmdb_id = tmdb.id

            await self.add_movie_genres(movie)
            await self.add_movie_countries(imdb_id, tmdb_id, movie)
            await self.mark_up(imdb_mvid)

            # await self.add_movie_productions(imdb_id, tmdb_id, movie)

            return ProductionData(imdb_id, tmdb_id, movie)

        except MovieDoesNotExist as ex:
            await self.mark_up(imdb_mvid)
            print(ex)

    async def add_all(self) -> None:
        async with self.mvdb.session as session:
            imdbs: list[IMDbORM] = await self.mvdb.get(
                IMDbORM,
                session,
                IMDbORM.id,
                IMDbORM.imdb_mvid,
                tmdb_added=False,
            )

            if len(imdbs) > 0:
                countries: list[CountryORM] = await self.mvdb.get(CountryORM, session)
                self.countries = {c.iso: c for c in countries}

                genres: list[GenreORM] = await self.mvdb.get(GenreORM, session)
                self.genres = {g.tmdb_name: g for g in genres}

                self.created_production_slugs = set()

        if len(imdbs) > 0:
            tasks = [self.add(m.id, m.imdb_mvid) for m in imdbs]

            print("Insert TMDb Movies")
            pdata: list[ProductionData] = await tqdm_asyncio.gather(*tasks)
            pdata: list[ProductionData] = [d for d in pdata if d is not None]

            await self.process_production_data(pdata)


async def main():
    adder = TMDbMovieAdder()
    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
