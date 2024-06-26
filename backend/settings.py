import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent
PROJ_DIR = ROOT_DIR.parent


def _check_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


class Settings(BaseSettings):
    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_NAME: str

    PG_POOL_SIZE: int
    PG_MAX_OVERFLOW: int

    DEBUG: bool
    MEDIA_DIR: str

    @property
    def PG_URL(self) -> str:
        return f"{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"

    @property
    def DSN_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.PG_URL}"

    @property
    def DSN_psycopg3(self) -> str:
        return f"postgresql+psycopg3://{self.PG_URL}"

    @property
    def MEDIA_PATH(self) -> str:
        return ROOT_DIR / self.MEDIA_DIR

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings(_env_file=PROJ_DIR / ".env")
_check_path(settings.MEDIA_PATH)
