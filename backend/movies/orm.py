import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    String,
    SmallInteger,
    BigInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))
from database.core import BaseORM, intpk


class MovieTypeORM(BaseORM):
    """IMDb movie type"""

    __tablename__ = "movie_type"

    id: Mapped[intpk]
    name_en: Mapped[str] = mapped_column(String(40))
    name_ru: Mapped[str] = mapped_column(String(40))

    ## relationships
    imdb_movies: Mapped[list["IMDbMovieORM"]] = relationship(
        back_populates="type",
    )

    __table_args__ = (
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
    )

    def __repr__(self) -> str:
        return self.name_en


class IMDbMovieORM(BaseORM):
    """IMDb movie info"""

    __tablename__ = "imdb_movie"

    id: Mapped[intpk]
    imdb_mvid: Mapped[str] = mapped_column(String(20))

    name_en: Mapped[str]
    name_ru: Mapped[str | None]
    slug: Mapped[str]

    is_adult: Mapped[bool]
    runtime: Mapped[int | None] = mapped_column(SmallInteger())

    rate: Mapped[float | None]
    wrate: Mapped[float | None]
    votes: Mapped[int | None]

    start_year: Mapped[int]
    end_year: Mapped[int | None]

    imdb_extra_added: Mapped[bool] = mapped_column(default=False)
    tmdb_added: Mapped[bool] = mapped_column(default=False)
    principals_added: Mapped[bool] = mapped_column(default=False)

    image_url: Mapped[str | None]

    ## Foreign Keys
    movie_type: Mapped[int | None] = mapped_column(
        ForeignKey(
            MovieTypeORM.id,
            ondelete="CASCADE",
        )
    )

    ## Relationships
    type: Mapped[MovieTypeORM] = relationship(back_populates="imdb_movies")
    tmdb: Mapped["TMDbMovieORM"] = relationship(back_populates="imdb")
    genres: Mapped[list["MovieGenreORM"]] = relationship(back_populates="imdb_movie")
    countries: Mapped[list["MovieCountryORM"]] = relationship(
        back_populates="imdb_movie"
    )
    production_companies: Mapped[list["MovieProductionORM"]] = relationship(
        back_populates="imdb_movie"
    )

    __table_args__ = (
        UniqueConstraint("imdb_mvid"),
        UniqueConstraint("slug"),
    )

    def __repr__(self) -> str:
        return str(self.imdb_mvid)


class MovieCollectionORM(BaseORM):
    """TMDb Collection"""

    __tablename__ = "collection"

    id: Mapped[intpk]
    tmdb_id: Mapped[int]

    name_en: Mapped[str]
    name_ru: Mapped[str | None]
    image_url: Mapped[str | None]

    ## relationships
    tmdb_movies: Mapped[list["TMDbMovieORM"]] = relationship(
        back_populates="collection",
    )

    __table_args__ = (UniqueConstraint("name_en"),)

    def __repr__(self) -> str:
        return self.name_en


class TMDbMovieORM(BaseORM):
    """TMDb movie info"""

    __tablename__ = "tmdb_movie"

    id: Mapped[intpk]
    tmdb_mvid: Mapped[int]

    release_date: Mapped[datetime | None]
    budget: Mapped[int | None] = mapped_column(BigInteger())
    revenue: Mapped[int | None] = mapped_column(BigInteger())
    image_url: Mapped[str | None]

    tagline_en: Mapped[str | None] = mapped_column(Text())
    overview_en: Mapped[str | None] = mapped_column(Text())

    tagline_ru: Mapped[str | None] = mapped_column(Text())
    overview_ru: Mapped[str | None] = mapped_column(Text())

    rate: Mapped[float | None]
    votes: Mapped[int | None]
    popularity: Mapped[float | None]

    ## Foreight Keys
    imdb_movie: Mapped[str] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    movie_collection: Mapped[int | None] = mapped_column(
        ForeignKey(
            MovieCollectionORM.id,
            ondelete="SET NULL",
        )
    )

    ## Relationships
    imdb: Mapped[IMDbMovieORM] = relationship(back_populates="tmdb")
    collection: Mapped[MovieCollectionORM] = relationship(back_populates="tmdb_movies")
    countries: Mapped[list["MovieCountryORM"]] = relationship(
        back_populates="tmdb_movie"
    )
    production_companies: Mapped[list["MovieProductionORM"]] = relationship(
        back_populates="tmdb_movie"
    )

    __table_args__ = (
        UniqueConstraint("tmdb_mvid"),
        UniqueConstraint("imdb_movie"),
    )

    def __repr__(self) -> str:
        return str(self.tmdb_mvid)


class CountryORM(BaseORM):
    __tablename__ = "country"

    id: Mapped[intpk]

    iso: Mapped[str]
    name_en: Mapped[str]
    name_ru: Mapped[str]
    image_url: Mapped[str | None]

    ## Relationships
    movies: Mapped[list["MovieCountryORM"]] = relationship(back_populates="country")
    productions: Mapped[list["ProductionCompanyORM"]] = relationship(
        back_populates="country_origin"
    )

    __table_args__ = (
        UniqueConstraint("iso"),
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
    )

    def __repr__(self) -> str:
        return self.name_en


class MovieCountryORM(BaseORM):
    __tablename__ = "movie_country"

    id: Mapped[intpk]

    # Foreign Keys
    country_id: Mapped[int] = mapped_column(
        ForeignKey(
            CountryORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    tmdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            TMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )

    ## Relationships
    imdb_movie: Mapped[IMDbMovieORM] = relationship(back_populates="countries")
    tmdb_movie: Mapped[TMDbMovieORM] = relationship(back_populates="countries")
    country: Mapped[CountryORM] = relationship(back_populates="movies")

    __table_args__ = (
        UniqueConstraint("country_id", "imdb_movie_id"),
        UniqueConstraint("country_id", "tmdb_movie_id"),
    )


class ProductionCompanyORM(BaseORM):
    __tablename__ = "production_company"

    id: Mapped[intpk]
    tmdb_id: Mapped[int]

    name_en: Mapped[str]
    slug: Mapped[str]
    image_url: Mapped[str | None]

    ## Foreign Keys
    country: Mapped[int | None] = mapped_column(
        ForeignKey(
            CountryORM.id,
            ondelete="CASCADE",
        )
    )

    ## Relationships
    country_origin: Mapped[CountryORM] = relationship(back_populates="productions")
    movies: Mapped[list["MovieProductionORM"]] = relationship(
        back_populates="production_company"
    )

    __table_args__ = (
        UniqueConstraint("name_en"),
        UniqueConstraint("slug"),
    )

    def __repr__(self) -> str:
        return str(self.name_en)


class MovieProductionORM(BaseORM):
    __tablename__ = "movie_production"

    id: Mapped[intpk]

    ## Foreign Keys
    production_company_id: Mapped[int] = mapped_column(
        ForeignKey(
            ProductionCompanyORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    tmdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            TMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )

    ## Relationships
    imdb_movie: Mapped[IMDbMovieORM] = relationship(
        back_populates="production_companies"
    )
    tmdb_movie: Mapped[TMDbMovieORM] = relationship(
        back_populates="production_companies"
    )
    production_company: Mapped[ProductionCompanyORM] = relationship(
        back_populates="movies"
    )

    __table_args__ = (
        UniqueConstraint("production_company_id", "imdb_movie_id"),
        UniqueConstraint("production_company_id", "tmdb_movie_id"),
    )


class GenreORM(BaseORM):
    __tablename__ = "genre"

    id: Mapped[intpk]

    name_en: Mapped[str]  # IMDb name
    name_ru: Mapped[str | None]

    slug: Mapped[str]

    tmdb_name: Mapped[str | None]
    image_url: Mapped[str | None]

    ## relations
    movies: Mapped[list["MovieGenreORM"]] = relationship(back_populates="genre")

    __table_args__ = (
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
        UniqueConstraint("slug"),
    )

    def __repr__(self) -> str:
        return str(self.name_en)


class MovieGenreORM(BaseORM):
    __tablename__ = "movie_genre"

    id: Mapped[intpk]

    imdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey(
            GenreORM.id,
            ondelete="CASCADE",
        )
    )

    ## relations
    imdb_movie: Mapped["IMDbMovieORM"] = relationship(back_populates="genres")
    genre: Mapped["GenreORM"] = relationship(back_populates="movies")

    __table_args__ = (UniqueConstraint("imdb_movie_id", "genre_id"),)
