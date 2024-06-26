from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from database import get_async_session
from operations.models import worker
from operations.schemas import WorkerCreate

worker_q = APIRouter(
    prefix="/worker",
    tags=["Worker"]
)

@worker_q.post("/create")
async def add_worker(new_worker: WorkerCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(worker).values(**new_worker.dict())
    result = await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@worker_q.get("/search")
async def get_worker(worker_name: str, session: AsyncSession = Depends(get_async_session)):
    query = select(worker).where(worker.c.fullname == worker_name)
    result = await session.execute(query)
    return result.mappings().all()

@worker_q.post("/update")
async def update_worker(name: str, login: str, passw: str, email: str, 
                             old_name: str, old_login: str, old_passw: str, old_email: str, 
                             session: AsyncSession = Depends(get_async_session)):
    stmt = update(worker).values(fullname=name, login=login, password=passw, email=email).where(
        worker.c.fullname == old_name, worker.c.login == old_login, worker.c.password == old_passw,
        worker.c.email == old_email)
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}