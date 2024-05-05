import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent


def _check_path(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)


class Settings(BaseSettings):
    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_NAME: str

    DEBUG: bool
    MEDIA_DIR: str

    @property
    def PG_URL(self) -> str:
        return f"{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_NAME}"

    @property
    def DSN_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.PG_URL}"

    @property
    def DSN_psycopg2(self) -> str:
        return f"postgresql+psycopg2://{self.PG_URL}"

    @property
    def MEDIA_PATH(self) -> str:
        return ROOT_DIR / self.MEDIA_DIR

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings(_env_file=ROOT_DIR / ".env")
_check_path(settings.MEDIA_PATH)
