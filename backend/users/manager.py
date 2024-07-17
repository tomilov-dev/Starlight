import sys
import uuid
import asyncio
from pathlib import Path
from typing import Any
from datetime import timedelta, datetime, timezone
from fastapi import Form, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
import bcrypt
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))

from settings import settings
from database.manager import DataBaseManager
from database.manager import AbstractMovieDataSource, AbstractPersonDataSource
from database.api import ExceptionToHandle
from movies.source import MovieDataSource
from movies.orm import IMDbMovieORM
from persons.source import PersonDataSource
from users.models import UserDTO, RegisterUserDTO, AuthUserDTO, TokenDTO
from users.orm import UserORM, UserMovieScoreORM


TOKEN_TYPE = "type"
ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"


class UserDoesNotExists(Exception):
    pass


class UserPasswordDoesNotMatch(Exception):
    pass


class UserNameExists(Exception):
    pass


class EmailExists(Exception):
    pass


class UserManager(DataBaseManager):
    ORM = UserORM

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

    def encode_jwt(
        self,
        payload: dict[str, Any],
        time_delta: timedelta,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.JWT_ALGORITHM,
    ) -> str:
        expire = datetime.now(timezone.utc) + time_delta
        payload.update(exp=expire, iat=datetime.now(timezone.utc), jti=uuid.uuid4().hex)
        return jwt.encode(payload, private_key, algorithm)

    def decode_jwt(
        self,
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.JWT_ALGORITHM,
    ) -> dict:
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
        return decoded

    def hash_password(self, password: str) -> bytes:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def validate_password(self, password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password)

    def create_access_token(self, user: UserDTO) -> str:
        return self.encode_jwt(
            {
                TOKEN_TYPE: ACCESS_TYPE,
                "sub": user.id,
                "username": user.username,
                "email": user.email,
            },
            time_delta=settings.auth_jwt.access_token_expire,
        )

    def create_refresh_token(self, user: UserDTO) -> str:
        return self.encode_jwt(
            {
                TOKEN_TYPE: REFRESH_TYPE,
                "sub": user.id,
            },
            time_delta=settings.auth_jwt.refresh_token_expire,
        )

    async def register(
        self,
        username: str,
        password: str,
        email: str,
    ) -> None:
        hashed_password = self.hash_password(password)
        async with self.dbapi.session as session:
            await self.dbapi.add(
                UserORM,
                session,
                _safe_add=False,
                _commit=True,
                username=username,
                hashed_password=hashed_password,
                email=email,
            )

    async def register_prevalidate(
        self,
        username: str,
        password: str,
        email: str,
    ) -> RegisterUserDTO:
        async with self.dbapi.session as session:
            if await self.dbapi.exists(
                UserORM,
                session,
                username=username,
            ):
                raise UserNameExists

            if await self.dbapi.exists(
                UserORM,
                session,
                email=email,
            ):
                raise EmailExists

        return RegisterUserDTO(
            username=username,
            password=password,
            email=email,
        )

    async def validate_user(self, username: str, password: str) -> UserDTO:
        async with self.dbapi.session as session:
            user: UserORM | None = await self.dbapi.get(
                UserORM,
                session,
                username=username,
            )

        if not user:
            raise UserDoesNotExists

        if not self.validate_password(password, user.hashed_password):
            raise UserPasswordDoesNotMatch

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            active=user.active,
        )

    async def get_user(self, user_id: int) -> UserDTO:
        async with self.dbapi.session as session:
            user_orm: UserORM = await self.dbapi.get(UserORM, session, id=user_id)
            return UserDTO(
                id=user_orm.id,
                username=user_orm.username,
                email=user_orm.email,
                active=user_orm.active,
            )

    async def add_movie_score(
        self,
        movie_id: int,
        user: UserDTO,
        score: int,
    ) -> None:
        async with self.dbapi.session as session:
            data = {"movie_id": movie_id, "user_id": user.id}
            if score is not None:
                data.update({"score": score})

            await self.dbapi.upsert(
                UserMovieScoreORM,
                session,
                conflict_attributes=["user_id", "movie_id"],
                **data
            )
