import redis

from fastapi import FastAPI

from utils import safe_key_builder

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from api.routes import router


app = FastAPI()
app.include_router(router, prefix='/api')


@app.on_event('startup')
async def startup():
    redis_client = redis.Redis(
        host='127.0.0.1', 
        port=6379, 
        db=0
    )

    FastAPICache.init(
        RedisBackend(redis_client),
        prefix= 'cache',
        key_builder=safe_key_builder
    )
