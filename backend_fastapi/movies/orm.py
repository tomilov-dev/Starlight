import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Annotated
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

from database.core import Base


intpk = Annotated[int, mapped_column(primary_key=True)]


class MovieTypeORM(Base):
    """IMDb movie type"""

    __tablename__ = "movie_type"

    id: Mapped[intpk]
    name_en: Mapped[str] = mapped_column(String(40))
    name_ru: Mapped[str] = mapped_column(String(40))

    ## relationships
    imdb_movies: Mapped[list["IMDbORM"]] = relationship(
        back_populates="type",
    )

    __table_args__ = (
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
    )

    def __repr__(self) -> str:
        return self.name_en


class IMDbORM(Base):
    """IMDb movie info"""

    __tablename__ = "imdb_movie"

    id: Mapped[intpk]

    imdb_mvid: Mapped[str] = mapped_column(String(20))
    movie_type: Mapped[int | None] = mapped_column(
        ForeignKey(
            MovieTypeORM.id,
            ondelete="CASCADE",
        )
    )

    title_en: Mapped[str]
    title_ru: Mapped[str | None]
    slug: Mapped[str]

    is_adult: Mapped[bool]
    runtime: Mapped[int | None] = mapped_column(SmallInteger())

    rate: Mapped[float | None]
    wrate: Mapped[float | None]
    votes: Mapped[int | None]

    imdb_extra_added: Mapped[bool] = mapped_column(default=False)
    tmdb_added: Mapped[bool] = mapped_column(default=False)
    image_url: Mapped[str | None]

    ## relationships
    tmdb: Mapped["TMDbORM"] = relationship(back_populates="imdb")
    type: Mapped[MovieTypeORM] = relationship(back_populates="imdb_movies")

    __table_args__ = (
        UniqueConstraint("imdb_mvid"),
        UniqueConstraint("slug"),
    )

    def __repr__(self) -> str:
        return str(self.imdb_mvid)


class CollectionORM(Base):
    """TMDb Collection"""

    __tablename__ = "collection"

    id: Mapped[intpk]
    name_en: Mapped[str]
    name_ru: Mapped[str | None]
    image_url: Mapped[str | None]

    ## relationships
    tmdb_movies: Mapped[list["TMDbORM"]] = relationship(
        back_populates="collection",
    )

    __table_args__ = (UniqueConstraint("name_en"),)

    def __repr__(self) -> str:
        return self.name_en


class TMDbORM(Base):
    """TMDb movie info"""

    __tablename__ = "tmdb_movie"

    id: Mapped[intpk]
    tmdb_mvid: Mapped[int]
    imdb_movie: Mapped[str] = mapped_column(
        ForeignKey(
            IMDbORM.id,
            ondelete="CASCADE",
        )
    )

    movie_collection: Mapped[int | None] = mapped_column(
        ForeignKey(
            CollectionORM.id,
            ondelete="SET NULL",
        )
    )

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

    ## relationships
    imdb: Mapped[IMDbORM] = relationship(back_populates="tmdb")
    collection: Mapped[CollectionORM] = relationship(back_populates="tmdb_movies")

    __table_args__ = (
        UniqueConstraint("tmdb_mvid"),
        UniqueConstraint("imdb_movie"),
    )

    def __repr__(self) -> str:
        return str(self.tmdb_mvid)


class CountryORM(Base):
    __tablename__ = "country"

    id: Mapped[intpk]

    iso: Mapped[str]
    name_en: Mapped[str]
    name_ru: Mapped[str]
    image_url: Mapped[str | None]

    __table_args__ = (
        UniqueConstraint("iso"),
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
    )


class MovieCountryORM(Base):
    __tablename__ = "movie_country"

    id: Mapped[intpk]

    country: Mapped[int] = mapped_column(
        ForeignKey(
            CountryORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbORM.id,
            ondelete="CASCADE",
        )
    )
    tmdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            TMDbORM.id,
            ondelete="CASCADE",
        )
    )

    __table_args__ = (
        UniqueConstraint("country", "imdb_movie"),
        UniqueConstraint("country", "tmdb_movie"),
    )


class ProductionCompanyORM(Base):
    __tablename__ = "production_company"

    id: Mapped[intpk]
    country: Mapped[int | None] = mapped_column(
        ForeignKey(
            CountryORM.id,
            ondelete="CASCADE",
        )
    )

    name_en: Mapped[str]
    slug: Mapped[str]
    image_url: Mapped[str | None]

    __table_args__ = (
        UniqueConstraint("name_en"),
        UniqueConstraint("slug"),
    )


class MovieProductionORM(Base):
    __tablename__ = "movie_production"

    id: Mapped[intpk]

    production_company: Mapped[int] = mapped_column(
        ForeignKey(
            ProductionCompanyORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbORM.id,
            ondelete="CASCADE",
        )
    )
    tmdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            TMDbORM.id,
            ondelete="CASCADE",
        )
    )

    __table_args__ = (
        UniqueConstraint("production_company", "imdb_movie"),
        UniqueConstraint("production_company", "tmdb_movie"),
    )


class GenreORM(Base):
    __tablename__ = "genre"

    id: Mapped[intpk]

    imdb_name: Mapped[str]
    slug: Mapped[str]

    tmdb_name: Mapped[str | None]
    name_ru: Mapped[str]

    image_url: Mapped[str | None]

    __table_args__ = (
        UniqueConstraint("imdb_name"),
        UniqueConstraint("name_ru"),
        UniqueConstraint("slug"),
    )


class MovieGenreORM(Base):
    __tablename__ = "movie_genre"

    id: Mapped[intpk]

    imdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbORM.id,
            ondelete="CASCADE",
        )
    )
    genre: Mapped[int] = mapped_column(
        ForeignKey(
            GenreORM.id,
            ondelete="CASCADE",
        )
    )

    __table_args__ = (UniqueConstraint("imdb_movie", "genre"),)
