from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


PROJ_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    PROXY: str
    TMDB_APIKEY: str
    TMDB_MAX_RATE: int
    TMDB_RATE_PERIOD: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings(_env_file=PROJ_DIR / ".env")
