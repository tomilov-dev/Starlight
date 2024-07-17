import sys
from pathlib import Path
from sqlalchemy import UniqueConstraint, ForeignKey, CheckConstraint, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from database.core import BaseORM
from movies.orm import IMDbMovieORM


class UserORM(BaseORM):
    __tablename__ = "usermodel"

    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[bytes]
    active: Mapped[bool] = True

    ## Relationships
    scores: Mapped[list["UserMovieScoreORM"]] = relationship(back_populates="user")

    __table_args__ = (
        UniqueConstraint("username"),
        UniqueConstraint("email"),
    )


class UserMovieScoreORM(BaseORM):
    __tablename__ = "user_movie_score"

    user_id: Mapped[int] = mapped_column(ForeignKey(UserORM.id))
    movie_id: Mapped[int] = mapped_column(ForeignKey(IMDbMovieORM.id))

    ## If score is NULL - it means user watched the movie but didn't rate it
    score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
        default=None,
    )

    ## Relationships
    user: Mapped[UserORM] = relationship(back_populates="scores")
    movie: Mapped[IMDbMovieORM] = relationship(back_populates="users_scores")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id"),
        CheckConstraint("score >= 0 AND score <= 10", name="score_range"),
    )


IMDbMovieORM.users_scores = relationship("UserMovieScoreORM", back_populates="movie")
