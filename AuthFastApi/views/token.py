# -*- coding: utf-8 -*-
import typing
import logging
import json

from fastapi import Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    HTTPBearer,
)

import schemas as schemas

from config import settings
from utils import create_access_token, verify_access_token
from app import redis_client, app

logger = logging.getLogger(__name__)

# Определяем схему OAuth2 для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

security = HTTPBearer()


async def get_user(username: str) -> schemas.User:
    """Получение данных о пользователе из БД"""

    user = await redis_client.hget("users", username)
    if user:
        data = json.loads(user)
        # возвращаем модель пользователя с хэшем пароля
        return schemas.User(**data)


async def add_user(username: str, password: str) -> schemas.User:
    """Добавление нового пользователя в БД"""

    logger.info(f"Add a new user into the database: {username}")
    await redis_client.hset(
        f"users",
        mapping={
            username: schemas.User(
                username=username, password=password
            ).model_dump_json()
        },
    )
    user = await redis_client.hget("users", username)
    data = json.loads(user)
    # возвращаем модель пользователя с хэшем пароля
    return schemas.User(**data)


async def authenticate_user(username: str, password: str) -> schemas.User:
    """Проверка подлинности и возврата пользователя"""

    logger.info(f"Request to check user in database: {username}")
    user = await get_user(username)
    # проверяем, получены ли данные пользователя
    if not user:
        hash_password = schemas.User.get_password_hash(password)
        new_user = await add_user(username, hash_password)
        return new_user
    # проверяем соответствие пароля и хэша пароля из базы данных
    if not schemas.User.verify_password(password, user.password):
        return
    return user


@app.post("/token", tags=["Token"])
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.Token:
    """
    Эндпоинт для получения JWT токена.
    При успешной аутентификации выдает access токен.
    """

    logger.info(f"Get token to user: {form_data.username}")
    user_identifier = await authenticate_user(form_data.username, form_data.password)
    if not user_identifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Находим токен пользователя
    access_token = await redis_client.hget("users_last_token", form_data.username)

    # Проверяем доступен ли токен
    exist_token = (
        await redis_client.hget("user_tokens", access_token) if access_token else None
    )
    if not exist_token:
        # Создаем токен с идентификатором пользователя (subject)
        access_token = create_access_token(
            {"sub": user_identifier.model_dump()},
            settings.SECRET_KEY,
            settings.ALGORITHM,
        )

        # Устанавливаем TTL (время жизни) для ключа в Redis, равное времени жизни токена.
        # Это гарантирует, что отозванный токен будет автоматически удален из Redis
        # по истечении его срока действия.
        token_expiry_seconds = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        await redis_client.hsetex(
            "user_tokens", mapping={access_token: "active"}, ex=token_expiry_seconds
        )

        # Меняем на новый последний токен пользователя
        await redis_client.hset(
            f"users_last_token", mapping={form_data.username: access_token}
        )

    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/new_token", tags=["Token"])
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.Token:
    """
    Эндпоинт для получения нового JWT токена.
    При успешной аутентификации выдает access токен.
    """

    logger.info(f"Get new token to user: {form_data.username}")
    user_identifier = await authenticate_user(form_data.username, form_data.password)
    logger.info(f"Check user: {user_identifier}")
    if not user_identifier:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Находим токен пользователя
    access_token = await redis_client.hget("users_last_token", form_data.username)

    # Удаляем сам токен
    await redis_client.hdel("user_tokens", access_token)

    # Создаем токен с идентификатором пользователя (subject)
    access_token = create_access_token(
        {"sub": user_identifier.model_dump()}, settings.SECRET_KEY, settings.ALGORITHM
    )
    # Устанавливаем TTL (время жизни) для ключа в Redis, равное времени жизни токена.
    # Это гарантирует, что отозванный токен будет автоматически удален из Redis
    # по истечении его срока действия.
    token_expiry_seconds = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    await redis_client.hsetex(
        f"user_tokens", mapping={access_token: "active"}, ex=token_expiry_seconds
    )

    # Меняем на новый последний токен пользователя
    await redis_client.hset(
        f"users_last_token", mapping={form_data.username: access_token}
    )

    return schemas.Token(access_token=access_token, token_type="bearer")


@app.post("/logout", tags=["Token"])
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Эндпоинт для выхода из системы. Удаляем данный токен из БД.
    """

    # Пороверяем есть ли активный токен для пользователя
    exist_token = await redis_client.hget("user_tokens", token)
    if not exist_token:
        return {"message": "Token didn't found"}

    # Получаем данные токена, чтобы убедиться, что он валиден перед удалением
    payload = verify_access_token(token, settings.SECRET_KEY, settings.ALGORITHM)
    if payload:
        await redis_client.hdel("user_tokens", token)
        return {"message": "Successfully logged out"}
    else:
        # Если токен невалиден, он уже не активен, но можно и уведомить.
        # Или просто проигнорировать, так как он уже не работает.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token provided for logout",
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Зависимость для получения текущего пользователя.
    Проверяет токен, ищет его в Redis (если используем blacklist/whitelist)
    и возвращает данные пользователя.
    """
    logger.info(f"Get user by token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token, settings.SECRET_KEY, settings.ALGORITHM)
    logger.info(f"User's payload from the token: {payload}")
    if payload is None:
        raise credentials_exception

    sub: str = payload.get("sub")  # Предполагаем, что 'sub' содержит имя пользователя
    logger.info(f"User's sub from the token: {sub}")
    if sub is None:
        raise credentials_exception

    # Проверяем доступен ли токен
    exist_token = await redis_client.hget("user_tokens", token)
    if not exist_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    sub = json.loads(sub)
    return schemas.User(**sub)  # Возвращаем имя пользователя


@app.get("/users/me", tags=["Token"], response_model=schemas.User)
async def read_users_me(
    user: typing.Annotated[schemas.User, Depends(get_current_user)],
):
    """Получение своих данных (авторизированного пользователя)"""

    return user
