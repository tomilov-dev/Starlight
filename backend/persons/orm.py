import sys
from pathlib import Path
from sqlalchemy import ForeignKey, UniqueConstraint, Column, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import BaseORM
from movies.orm import IMDbMovieORM


class IMDbPersonORM(BaseORM):
    """IMDb person"""

    __tablename__ = "imdb_person"

    imdb_nmid: Mapped[str]
    name_en: Mapped[str]
    slug: Mapped[str]

    birth_y: Mapped[int | None]
    death_y: Mapped[int | None]
    image_url: Mapped[str | None]

    tmdb_added: Mapped[bool] = mapped_column(default=False)
    imdb_extra_added: Mapped[bool] = mapped_column(default=False)

    ## relationships
    tmdb: Mapped["TMDbPersonORM"] = relationship(back_populates="imdb")
    professions: Mapped[list["PersonProfessionORM"]] = relationship(
        back_populates="person"
    )
    movies: Mapped[list["MoviePrincipalORM"]] = relationship(
        back_populates="imdb_person"
    )

    __table_args__ = (
        UniqueConstraint("imdb_nmid"),
        UniqueConstraint("slug"),
    )


class ProfessionORM(BaseORM):
    """Profession from IMDb"""

    __tablename__ = "profession"

    imdb_name: Mapped[str]
    name_en: Mapped[str]
    name_ru: Mapped[str]

    ## relations
    persons_by_profession: Mapped[list["PersonProfessionORM"]] = relationship(
        back_populates="profession"
    )
    movies_by_profession: Mapped[list["MoviePrincipalORM"]] = relationship(
        back_populates="profession"
    )

    __table_args__ = (
        UniqueConstraint("imdb_name"),
        UniqueConstraint("name_en"),
        UniqueConstraint("name_ru"),
    )


class PersonProfessionORM(BaseORM):
    """Person Profession from IMDb"""

    __tablename__ = "person_profession"

    ## Foreign Keys
    profession_id: Mapped[int] = mapped_column(
        ForeignKey(
            ProfessionORM.id,
            ondelete="CASCADE",
        )
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )

    ## relations
    person: Mapped["IMDbPersonORM"] = relationship(back_populates="professions")
    profession: Mapped["ProfessionORM"] = relationship(
        back_populates="persons_by_profession"
    )

    __table_args__ = (UniqueConstraint("profession_id", "person_id"),)


class MoviePrincipalORM(BaseORM):
    """Principal of IMDb Movie"""

    __tablename__ = "movie_principal"

    ordering: Mapped[int]
    job: Mapped[str | None]
    characters: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=True)

    ## Foreign Keys
    imdb_movie_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_person_id: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )
    # it is IMDb 'name' of profession
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            ProfessionORM.id,
            ondelete="SET NULL",
        )
    )

    ## Relationships
    imdb_movie: Mapped[IMDbMovieORM] = relationship(back_populates="principals")
    imdb_person: Mapped[IMDbPersonORM] = relationship(back_populates="movies")
    profession: Mapped[ProfessionORM] = relationship(
        back_populates="movies_by_profession"
    )

    # UniqueConstraint("imdb_person_id", "category_id"),
    __table_args__ = (
        UniqueConstraint("imdb_movie_id", "imdb_person_id", "category_id"),
    )


class TMDbPersonORM(BaseORM):
    """TMDb person"""

    __tablename__ = "tmdb_person"

    tmdb_nmid: Mapped[int]

    name_en: Mapped[str]
    name_ru: Mapped[str | None]

    gender: Mapped[int]

    ## Foreign Keys
    imdb_person: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )

    ## Relationships
    imdb: Mapped["IMDbPersonORM"] = relationship(back_populates="tmdb")

    __table_args__ = (
        UniqueConstraint("tmdb_nmid"),
        UniqueConstraint("imdb_person"),
    )


IMDbMovieORM.principals = relationship("MoviePrincipalORM", back_populates="imdb_movie")
