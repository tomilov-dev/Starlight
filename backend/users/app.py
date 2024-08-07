import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from users.models import UserDTO, TokenDTO, RegisterUserDTO, AuthUserDTO
from users.manager import (
    UserManager,
    TOKEN_TYPE,
    ACCESS_TYPE,
    REFRESH_TYPE,
    UserDoesNotExists,
    UserPasswordDoesNotMatch,
    EmailExists,
    UserNameExists,
)


router = APIRouter()
manager = UserManager()


http_bearer = HTTPBearer()


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    return credentials.credentials


def validate_token(token: str, token_type: str) -> dict:
    payload = manager.decode_jwt(token)
    if payload[TOKEN_TYPE] != token_type:
        raise HTTPException(401, f"Invalid token: {token_type} token required")
    return payload


def get_user_id(payload: dict) -> str:
    user_id = payload.get("sub", None)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    return user_id


async def get_user_for_access(token: str = Depends(get_token)) -> UserDTO:
    payload = validate_token(token, ACCESS_TYPE)
    user_id = get_user_id(payload)
    user = await manager.get_user(user_id)
    return user


async def get_user_for_refresh(token: str = Depends(get_token)) -> UserDTO:
    payload = validate_token(token, REFRESH_TYPE)
    user_id = get_user_id(payload)
    user = await manager.get_user(user_id)
    return user


async def validate_user(
    username: str = Form(),
    password: str = Form(),
) -> UserDTO | None:
    try:
        unauthed_exc = HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )
        return await manager.validate_user(username, password)

    except UserDoesNotExists:
        raise unauthed_exc

    except UserPasswordDoesNotMatch:
        raise unauthed_exc


async def register_prevalidate(
    username: str = Form(),
    password: str = Form(),
    email: str = Form(),
):
    try:
        return await manager.register_prevalidate(username, password, email)

    except UserNameExists:
        raise HTTPException(400, detail="Username exists")

    except EmailExists:
        raise HTTPException(400, detail="Email exists")


@router.post("/users/register")
async def register(
    user_create: RegisterUserDTO = Depends(register_prevalidate),
):
    await manager.register(
        username=user_create.username,
        password=user_create.password,
        email=user_create.email,
    )


@router.post("/users/login", response_model=TokenDTO)
async def login(user: UserDTO = Depends(validate_user)):
    access_token = manager.create_access_token(user)
    refresh_token = manager.create_refresh_token(user)
    return TokenDTO(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/users/refresh",
    response_model=TokenDTO,
    response_model_exclude_none=True,
)
async def refresh_token(user: UserDTO = Depends(get_user_for_refresh)):
    access_token = manager.create_access_token(user)
    return TokenDTO(access_token=access_token)


@router.get("/users/me")
async def user_check(user: UserDTO | None = Depends(get_user_for_access)):
    if user:
        return user
    return "Hello, stranger!"


@router.post("/users/score")
async def score_the_movie(
    movie_id: int = Form(),
    score: int = Form(ge=0, le=10),
    user: UserDTO = Depends(get_user_for_access),
):
    await manager.add_movie_score(movie_id, user, score)


@router.post("/users/watched")
async def mark_movie_as_watched(
    movie_id: int = Form(),
    user: UserDTO = Depends(get_user_for_access),
):
    await manager.add_movie_score(movie_id, user, score=None)
