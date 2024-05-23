from fastapi import FastAPI
from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate
from operations.router import worker_q as router_worker
from operations.router import typeVication as router_typeVication
from operations.router import post_q as router_post
from operations.router import dept_q as router_dept
from operations.router import vication_q as router_vication

app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_worker)
app.include_router(router_typeVication)
app.include_router(router_post)
app.include_router(router_dept)
app.include_router(router_vication)