# -*- coding: utf-8 -*-
import redis.asyncio as redis
import logging
import fastapi

from fastapi_limiter import FastAPILimiter

import logging.handlers as l_handl

# import uvicorn
from config import settings

rot_file_handler = l_handl.RotatingFileHandler(
    settings.LOG_FILE_PATH, maxBytes=50 * 1024 * 1024, backupCount=10, encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    handlers=[rot_file_handler],
    format=(
        "[%(asctime)s] (%(filename)s:%(lineno)d %(threadName)s) "
        '%(levelname)s - %(name)s: "%(message)s"'
    ),
)

app = fastapi.FastAPI(**settings.api_metadata, debug=True)

# Инициализация клиента Redis
redis_client = redis.Redis(
    host=settings.redis_dsn.host,
    port=settings.redis_dsn.port,
    decode_responses=True,  # Декодируем ответы из байт в строки
)


@app.on_event("startup")
async def startup():

    await FastAPILimiter.init(redis_client)


from views import *
