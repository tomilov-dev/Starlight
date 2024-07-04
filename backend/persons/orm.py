import sys
from pathlib import Path
from sqlalchemy import ForeignKey, UniqueConstraint, Column, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import BaseORM
from movies.orm import intpk, IMDbMovieORM


class IMDbPersonORM(BaseORM):
    """IMDb person"""

    __tablename__ = "imdb_person"

    id: Mapped[intpk]

    imdb_nmid: Mapped[str]
    name_en: Mapped[str]
    slug: Mapped[str]
    birth_y: Mapped[int | None]
    death_y: Mapped[int | None]
    image_url: Mapped[str | None]

    tmdb_added: Mapped[bool] = mapped_column(default=False)
    imdb_extra_added: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        UniqueConstraint("imdb_nmid"),
        UniqueConstraint("slug"),
    )


class TMDbPersonORM(BaseORM):
    """TMDb person"""

    __tablename__ = "tmdb_person"

    id: Mapped[intpk]

    imdb_person: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )
    tmdb_nmid: Mapped[int]

    name_en: Mapped[str]
    name_ru: Mapped[str | None]

    gender: Mapped[int]

    __table_args__ = (
        UniqueConstraint("tmdb_nmid"),
        UniqueConstraint("imdb_person"),
    )


class ProfessionORM(BaseORM):
    """Profession from IMDb"""

    __tablename__ = "profession"

    id: Mapped[intpk]
    imdb_name: Mapped[str]
    name_en: Mapped[str]
    name_ru: Mapped[str]

    __table_args__ = (UniqueConstraint("imdb_name"),)


class PersonProfessionORM(BaseORM):
    """Person Profession from IMDb"""

    __tablename__ = "person_profession"

    id: Mapped[intpk]
    profession: Mapped[int] = mapped_column(
        ForeignKey(
            ProfessionORM.id,
            ondelete="CASCADE",
        )
    )
    person: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )


class MoviePrincipalORM(BaseORM):
    """Principal of IMDb Movie"""

    __tablename__ = "movie_principal"

    id: Mapped[intpk]

    imdb_movie: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbMovieORM.id,
            ondelete="CASCADE",
        )
    )
    imdb_person: Mapped[int] = mapped_column(
        ForeignKey(
            IMDbPersonORM.id,
            ondelete="CASCADE",
        )
    )
    category: Mapped[int | None] = mapped_column(
        ForeignKey(
            ProfessionORM.id,
            ondelete="SET NULL",
        )
    )

    ordering: Mapped[int]
    job: Mapped[str | None]
    charachters = Column(ARRAY(String), nullable=True)
