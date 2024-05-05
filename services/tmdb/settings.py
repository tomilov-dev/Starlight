from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


ROOT_DIR = Path(__file__).parent


class Settings(BaseSettings):
    APIKEY: str
    TEST_PROXY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings(_env_file=ROOT_DIR / ".env")
