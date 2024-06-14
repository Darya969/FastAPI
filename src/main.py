from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from operations.worker_q import worker_q as router_worker
from operations.typeVication import typeVication as router_typeVication
from operations.post_q import post_q as router_post
from operations.dept_q import dept_q as router_dept
from operations.router import vication_q as router_vication

app = FastAPI()

app.include_router(router_worker)
app.include_router(router_typeVication)
app.include_router(router_post)
app.include_router(router_dept)
app.include_router(router_vication)

origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Assert-Control-Allow-Headers", "Access-Control-Allow-Origin", "Authorization"],
)

# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
