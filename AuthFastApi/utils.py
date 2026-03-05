import json
import logging

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from config import settings

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Если объекта еще нет, создаем его
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def create_access_token(data: dict, secret_key: str, algorithm: str) -> str:
    """Создает JWT access токен"""
    to_encode = data.copy()
    to_encode["sub"] = json.dumps(to_encode["sub"])
    # Добавляем время жизни токена
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(token: str, secret_key: str, algorithm: str) -> dict | None:
    """Верифицирует JWT access токен и возвращает данные из него"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        # Проверка на наличие необходимых полей, например, 'sub' (subject)
        if payload.get("sub"):
            return payload
    except JWTError as e:
        logger.error(e)
        return None
    return None
