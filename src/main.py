from fastapi import FastAPI
from operations.router import worker_q as router_worker
from operations.router import typeVication as router_typeVication
from operations.router import post_q as router_post
from operations.router import dept_q as router_dept
from operations.router import vication_q as router_vication

app = FastAPI()

app.include_router(router_worker)
app.include_router(router_typeVication)
app.include_router(router_post)
app.include_router(router_dept)
app.include_router(router_vication)