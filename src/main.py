from fastapi import FastAPI
from operations.router import router as router_operation

app = FastAPI()

app.include_router(router_operation)