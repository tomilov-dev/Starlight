import sys
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
PROJ_DIR = ROOT_DIR.parent
sys.path.append(str(ROOT_DIR))
sys.path.append(str(PROJ_DIR))

from data.adder import DatabaseAdder
from services.tmdb.scraper import TMDbScraper, TMDbMovie, Production, MovieDoesNotExist
from services.tmdb.settings import settings
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
    45,
    1,
)


class TMDbMovieAdder(DatabaseAdder):
    def __init__(self) -> None:
        super().__init__()

        self.scraper = SCRAPER

    async def mark_up(self, imdb_mvid: str) -> None:
        await self.mvdb.update(
            IMDbORM,
            filters={"imdb_mvid": imdb_mvid},
            tmdb_added=True,
        )

    async def add_production(
        self,
        production: Production,
        country: CountryORM,
    ) -> ProductionCompanyORM:
        init_slug = self.mvdb.initiate_slug(
            production.name,
            self.created_production_slugs,
        )
        slug = await self.mvdb.create_slug(init_slug, ProductionCompanyORM)

        country = country.id if country else country

        production = ProductionCompanyORM(
            country=country,
            name_en=production.name,
            slug=slug,
            image_url=production.image_url,
        )
        production = await self.mvdb.goc(
            production,
            ProductionCompanyORM,
            name_en=production.name_en,
        )
        return production

    async def add_movie_productions(
        self,
        imdb_id: int,
        tmdb_id: int,
        movie: TMDbMovie,
    ) -> None:
        productions = movie.productions

        if productions:
            for production in productions:
                country = self.countries.get(production.country, None)
                production = await self.add_production(
                    production,
                    country,
                )

                movie_production = MovieProductionORM(
                    production_company=production.id,
                    imdb_movie=imdb_id,
                    tmdb_movie=tmdb_id,
                )
                await self.mvdb.insert_movie_production(movie_production)

    async def add_movie_countries(
        self,
        imdb_id: int,
        tmdb_id: int,
        movie: TMDbMovie,
    ) -> None:
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

        await self.mvdb.insertb_movie_countries(movie_countries)

    async def add_movie_genres(self, movie: TMDbMovie) -> None:
        genres = [self.genres[g] for g in movie.genres]
        for genre in genres:
            await self.mvdb.insert(genre)

    def setup_tmdb(
        self,
        movie: TMDbMovie,
        imdb_id: int,
        collection: int | None,
    ) -> TMDbORM:
        return TMDbORM(
            tmdb_mvid=movie.tmdb_mvid,
            imdb_movie=imdb_id,
            movie_collection=collection,
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
    ) -> None:
        try:
            movie: TMDbMovie = await self.scraper.get_movie(imdb_mvid)

            collection = None
            if movie.collection:
                collection = CollectionORM(
                    name_en=movie.collection.name_en,
                    name_ru=movie.collection.name_ru,
                )

                ### -----  ERROR  -----

                ## Здесь возникает ошибка связанная с обработкой
                ## исключения IntegrityError внутри 'goc'
                ## а также ошибок на уровне insert (InvalidRequestError)
                ## возникает, потому что на момент проверки
                ## записи не существует, но на момент создания
                ## запись существует и не позволяет создать новую

                ## последний статус: исправлено, работало
                ## предположительно возникала вследствие
                ## InvalidRequestError и падения всего цикла
                ## из-за косвенных причин

                collection: CollectionORM = await self.mvdb.goc(
                    collection,
                    CollectionORM,
                    name_en=collection.name_en,
                )
                collection = collection.id

                ### -----  ERROR  -----

            tmdb = self.setup_tmdb(movie, imdb_id, collection)
            tmdb: TMDbORM = await self.mvdb.goc(
                tmdb,
                TMDbORM,
                tmdb_mvid=tmdb.tmdb_mvid,
            )
            tmdb_id = tmdb.id

            await self.add_movie_genres(movie)
            await self.add_movie_countries(imdb_id, tmdb_id, movie)
            await self.add_movie_productions(imdb_id, tmdb_id, movie)
            await self.mark_up(imdb_mvid)

        except MovieDoesNotExist as ex:
            await self.mark_up(imdb_mvid)
            print(ex)

    async def add_all(self) -> None:
        imdb: IMDbORM = await self.mvdb.get(
            IMDbORM,
            IMDbORM.id,
            IMDbORM.imdb_mvid,
            tmdb_added=False,
        )

        if len(imdb) > 0:
            countries: list[CountryORM] = await self.mvdb.get(CountryORM)
            self.countries = {c.iso: c for c in countries}

            genres: list[GenreORM] = await self.mvdb.get(GenreORM)
            self.genres = {g.tmdb_name: g for g in genres}

            self.created_production_slugs = set()

            tasks = [self.add(m.id, m.imdb_mvid) for m in imdb]
            await asyncio.gather(*tasks)


async def main():
    adder = TMDbMovieAdder()
    await adder.add_all()


if __name__ == "__main__":
    asyncio.run(main())
