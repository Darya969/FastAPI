from fastapi import FastAPI
from operations.worker_q import worker_q as router_worker
from operations.typeVication import typeVication as router_typeVication
from operations.post_q import post_q as router_post
from operations.dept_q import dept_q as router_dept
from operations.vication_q import vication_q as router_vication

app = FastAPI()

app.include_router(router_worker)
app.include_router(router_typeVication)
app.include_router(router_post)
app.include_router(router_dept)
app.include_router(router_vication)