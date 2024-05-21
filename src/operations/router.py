from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, exists, and_
from database import get_async_session
from operations.models import worker, typevication, post, dept
from operations.schemas import WorkerCreate, TypeCreate, PostCreate

router = APIRouter(
    prefix="/operations",
    tags=["Operation"]
)

@router.post("/worker_create")
async def post_worker(new_worker: WorkerCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(worker).values(**new_worker.dict())
    result = await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@router.get("/worker_search")
async def get_worker(worker_name: str, session: AsyncSession = Depends(get_async_session)):
    query = select(worker).where(worker.c.fullname == worker_name)
    result = await session.execute(query)
    return result.mappings().all()

@router.post("/worker_update")
async def post_worker_update(name: str, login: str, passw: str, email: str, 
                             old_name: str, old_login: str, old_passw: str, old_email: str, 
                             session: AsyncSession = Depends(get_async_session)):
    stmt = update(worker).values(fullname=name, login=login, password=passw, email=email).where(
        worker.c.fullname == old_name, worker.c.login == old_login, worker.c.password == old_passw,
        worker.c.email == old_email)
    result = await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@router.post('/typeVication_create')
async def add_typeVication(new_typeVication: TypeCreate, session: AsyncSession = Depends(get_async_session)):
    stmt =  insert(typevication).values(**new_typeVication.dict())
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@router.get("/typeVication_search")
async def get_typeVication(session: AsyncSession = Depends(get_async_session)):
    query = select(typevication)
    result = await session.execute(query)
    return result.mappings().all()

@router.post('/post_create')
async def add_post(new_post: PostCreate, session: AsyncSession = Depends(get_async_session)):
    stmt =  insert(post).values(**new_post.dict())
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@router.get("/post_search")
async def get_post(session: AsyncSession = Depends(get_async_session)):
    query = select(post)
    result = await session.execute(query)
    return result.mappings().all()

@router.post('/dept_create')
async def add_dept(id: int, new_title: str, new_worker: str, new_post: str, 
                   session: AsyncSession = Depends(get_async_session)):
    
    worker_id = select(worker.c.id).where(worker.c.fullname == new_worker)
    post_id = select(post.c.id).where(post.c.title == new_post)

    # Проверяем есть ли уже такой worker_id в new_title
    worker_exists = await session.execute(select(dept).filter(dept.c.title == new_title, dept.c.worker_id == worker_id))
    worker_exists = worker_exists.scalars().first()

    if worker_exists:
        return {'status': 'Error', 'message': f'Сотрудник "{new_worker}" уже существует в отделе "{new_title}".'}
    
    # Проверяем есть ли уже такой worker_id в new_title
    post_exists = await session.execute(select(dept).filter(dept.c.title == new_title, dept.c.post_id == post_id))
    post_exists = post_exists.scalars().first()
    
    if post_exists:
        return {'status': 'Error', 'message': f'Должность "{new_post}" в отделе "{new_title}" уже занята.'}
    
    stmt = insert(dept).values(id=id, title=new_title, worker_id=worker_id, post_id=post_id)
    await session.execute(stmt)
    await session.commit()
    
    return {'status': 'OK'}

@router.get("/dept_search")
async def get_dept(dept_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(dept.c.id, dept.c.title, worker.c.fullname, post.c.title).select_from(
    dept.join(worker, worker.c.id == dept.c.worker_id).join(post, post.c.id == dept.c.post_id)).\
        where(dept.c.title == dept_title)
    result = await session.execute(query)
    return result.mappings().all()