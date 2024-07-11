from typing import ClassVar, Optional

from pydantic import ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PYTEST_XDIST_WORKER: str = ""

    # DB config
    POSTGRES_DB_URI: str
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar = {"pool_size": 100}

    # Application
    AUTH_SECRET_KEY: str = "CHANGEME"
    ACCESS_TOKEN_LIFESPAN_MINUTES: int = 60 * 24 * 30  # Around a month, dummy value

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def set_uri(cls, value, info: ValidationInfo):
        if value:
            return value

        base_uri = info.data["POSTGRES_DB_URI"]
        parallel_worker = info.data.get("PYTEST_XDIST_WORKER", "")
        return base_uri + parallel_worker[-1] if parallel_worker else base_uri


settings = Settings()


def get_settings() -> Settings:
    return Settings()
