from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, or_
from database import get_async_session
from operations.models import worker

worker_q = APIRouter(
    prefix="/worker",
    tags=["Worker"]
)

@worker_q.post("/create")
async def add_worker(surname: str, name: str, patronymic: str, login: str, password: str, email: str,
                     session: AsyncSession = Depends(get_async_session)):
    stmt = insert(worker).values(surname=surname, name=name, patronymic=patronymic, login=login, 
                                 password=password, email=email)
    result = await session.execute(stmt)
    await session.commit()

    new_worker = select(worker).where(worker.c.surname == surname, worker.c.name == name, 
                                      worker.c.patronymic == patronymic, worker.c.email == email)
    insert_worker = await session.execute(new_worker)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}

@worker_q.get("/search")
async def get_worker(worker_surname: str | None = None, worker_name: str | None = None, 
                     worker_patronymic: str | None = None, worker_email: str | None = None, 
                     session: AsyncSession = Depends(get_async_session)):
    query = select(worker).where(or_(worker.c.surname == worker_surname, worker.c.name == worker_name, 
                                     worker.c.patronymic == worker_patronymic, worker.c.email == worker_email))
    result = await session.execute(query)
    return result.mappings().all()

@worker_q.post("/update")
async def update_worker(old_worker_id: int, surname: str | None = None, name: str | None = None, 
                        patronymic: str | None = None, login: str | None = None,  passw: str | None = None, 
                        email: str | None = None, session: AsyncSession = Depends(get_async_session)):
    update_data = {}
    if surname is not None:
        update_data['surname'] = surname
    if name is not None:
        update_data['name'] = name
    if patronymic is not None:
        update_data['patronymic'] = patronymic
    if login is not None:
        update_data['login'] = login
    if passw is not None:
        update_data['passw'] = passw
    if email is not None:
        update_data['email'] = email

    if update_data:
        stmt = (update(worker).where(worker.c.id == old_worker_id).values(**update_data).returning(worker))
        result = await session.execute(stmt)
        await session.commit()

    update_worker = select(worker).where(worker.c.id == old_worker_id)
    insert_worker = await session.execute(update_worker)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}