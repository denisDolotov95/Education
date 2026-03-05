# -*- coding: utf-8 -*-
import os
import json
import secrets
# from pydantic import BaseModel

from pydantic import (
    AliasChoices,
    AmqpDsn,
    BaseModel,
    Field,
    ImportString,
    PostgresDsn,
    RedisDsn,
)

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Время жизни access токена в минутах
    LOG_FILE_PATH: str = "./app.log"
    # Секретный ключ для подписи JWT токенов
    SECRET_KEY: str = os.environ.get("FAST_API_SECRET_KEY", secrets.token_hex(256))
    ALGORITHM: str = "HS256"
    
    # Настройки Redis
    redis_dsn: RedisDsn = Field(
        "redis://user:pass@localhost:6379/1",
        validation_alias=AliasChoices("REDIS_URL"),
    )
    # Настройка Postgres
    # pg_dsn: PostgresDsn = Field(
    #     "postgresql+asyncpg://postgres:postgres@localhost:5440/stepik",
    #     validation_alias=AliasChoices("POSTGRES_URL"),
    # )
    # Метаданные для свагера
    api_metadata: dict = json.loads(
        open("./api_metadata.json", "r", encoding="utf-8").read()
    )

    # class Config:
    #     env_file = ".env" # Файл с переменными окружения, если используется
    #     env_file_encoding = 'utf-8'


settings = Settings()
