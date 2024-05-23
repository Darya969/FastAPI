from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, exists, and_, or_, func
from database import get_async_session
from operations.models import worker, typevication, post, dept, vicaion
from operations.schemas import WorkerCreate, TypeCreate, PostCreate
from datetime import datetime

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

typeVication = APIRouter(
    prefix="/typeVication",
    tags=["Type vication"]
)

@typeVication.post('/create')
async def add_typeVication(new_typeVication: TypeCreate, session: AsyncSession = Depends(get_async_session)):
    stmt =  insert(typevication).values(**new_typeVication.dict())
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@typeVication.get("/search")
async def get_typeVication(session: AsyncSession = Depends(get_async_session)):
    query = select(typevication)
    result = await session.execute(query)
    return result.mappings().all()

@typeVication.post('/update')
async def update_typeVication(title: str, old_title: str, session: AsyncSession = Depends(get_async_session)):
    stmt =  update(typevication).values(title=title).where(typevication.c.title == old_title)
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

post_q = APIRouter(
    prefix="/post",
    tags=["Post"]
)

@post_q.post('/create')
async def add_post(new_post: PostCreate, session: AsyncSession = Depends(get_async_session)):
    stmt =  insert(post).values(**new_post.dict())
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

@post_q.get("/search")
async def get_post(session: AsyncSession = Depends(get_async_session)):
    query = select(post)
    result = await session.execute(query)
    return result.mappings().all()

@post_q.post('/update')
async def update_post(title: str, old_title: str, session: AsyncSession = Depends(get_async_session)):
    stmt =  update(post).values(title=title).where(post.c.title == old_title)
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}

dept_q = APIRouter(
    prefix="/dept",
    tags=["Dept"]
)

@dept_q.post('/create')
async def add_dept(id: int, new_title: str, new_worker: str, new_post: str, 
                   session: AsyncSession = Depends(get_async_session)):
    
    stmt_worker_id = select(worker.c.id).where(worker.c.fullname == new_worker)
    stmt_post_id = select(post.c.id).where(post.c.title == new_post)

    stmt_existing_worker = select(dept.c.id).where(dept.c.worker_id == stmt_worker_id)
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Сотрудник "{new_worker}" уже существует.'}

    if new_post == "руководитель" or new_post == "главный бухгалтер":
        stmt_post_count = select(func.count()).where(
            and_(dept.c.title == new_title, post.c.title == new_post)
        )
        post_count = await session.execute(stmt_post_count)
        if post_count.scalar() > 1:
            return {'status': 'Error', 'message': f'В "{new_title}" должность "{new_post}" уже занята.'}

    stmt = insert(dept).values(id=id, title=new_title, worker_id=stmt_worker_id, post_id=stmt_post_id)
    await session.execute(stmt)
    await session.commit()
    
    return {'status': 'OK'}

@dept_q.get("/search")
async def get_dept(dept_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(dept.c.id, dept.c.title, worker.c.fullname, post.c.title).select_from(
    dept.join(worker, worker.c.id == dept.c.worker_id).join(post, post.c.id == dept.c.post_id)).\
        where(dept.c.title == dept_title)
    result = await session.execute(query)
    return result.mappings().all()

@dept_q.post('/update')
async def update_dept(new_title: str, worker_n: str, post_n: str, old_title: str, old_worker: str, 
                      old_post: str, session: AsyncSession = Depends(get_async_session)):
    
    post_exists = await session.execute(select(dept).where(and_(dept.c.title == new_title, or_(dept.c.post_id == 1, dept.c.post_id == 2))))
    post_exists = post_exists.fetchall()

    if post_n == "руководитель" or post_n == "главный бухгалтер":
        stmt_post_count = select(func.count()).where(
            and_(dept.c.title == new_title, post.c.title == post_n)
        )
        post_count = await session.execute(stmt_post_count)
        if post_count.scalar() > 1:
            return {'status': 'Error', 'message': f'В "{new_title}" должность "{post_n}" уже занята.'}
    
    stmt_worker_id_new = select(worker.c.id).where(worker.c.fullname == worker_n)
    stmt_post_id_new = select(post.c.id).where(post.c.title == post_n)

    stmt_worker_id_old = select(worker.c.id).where(worker.c.fullname == old_worker)
    stmt_post_id_old = select(post.c.id).where(post.c.title == old_post)
   
    stmt_update = update(dept) \
        .where(and_(dept.c.title == old_title,
                    dept.c.worker_id == stmt_worker_id_old, dept.c.post_id == stmt_post_id_old)) \
        .values(title=new_title, worker_id=stmt_worker_id_new, post_id=stmt_post_id_new)
    await session.execute(stmt_update)
    await session.commit()
    return {'status': 'OK'}

vication_q = APIRouter(
    prefix="/vication",
    tags=["Vication"]
)

@vication_q.post("/create")
async def add_vication(id: int, new_typevication: str, new_worker: str, new_startdate: str, new_enddate: str,
                   session: AsyncSession = Depends(get_async_session)):
    
    stmt_typevication_id = select(typevication.c.id).where(typevication.c.title == new_typevication)
    stmt_worker_id = select(worker.c.id).where(worker.c.fullname == new_worker)

    new_startdate = datetime.strptime(new_startdate, '%Y-%m-%d').date()
    new_enddate = datetime.strptime(new_enddate, '%Y-%m-%d').date()

    stmt_overlap_count = select(func.count()).where(
        and_(
            vicaion.c.worker_id == stmt_worker_id,
            or_(
                and_(vicaion.c.startdate <= new_startdate, vicaion.c.enddate >= new_startdate),
                and_(vicaion.c.startdate <= new_enddate, vicaion.c.enddate >= new_enddate),
                and_(vicaion.c.startdate >= new_startdate, vicaion.c.enddate <= new_enddate)
            )
        )
    )

    overlap_count = await session.execute(stmt_overlap_count)
    if overlap_count.scalar() > 0:
        return {'status': 'Error', 'message': f'Пересечение дат в {new_typevication} у {new_worker}.'}

    stmt = insert(vicaion).values(id=id, typevication_id=stmt_typevication_id, worker_id=stmt_worker_id, 
                               startdate=new_startdate, enddate=new_enddate)
    await session.execute(stmt)
    await session.commit()
    
    return {'status': 'OK'}

@vication_q.get("/search")
async def get_vication(name: str, session: AsyncSession = Depends(get_async_session)):
    query = select(vicaion.c.id, typevication.c.title, worker.c.fullname, vicaion.c.startdate, 
                   vicaion.c.enddate).select_from(
        vicaion.join(typevication, typevication.c.id == vicaion.c.typevication_id)
        .join(worker, worker.c.id == vicaion.c.worker_id)).\
        where(worker.c.fullname == name)
    result = await session.execute(query)
    return result.mappings().all()

@vication_q.post("/update")
async def update_vication(new_typevication: str, new_worker: str, new_startdate: str, new_enddate: str,
                          old_typevication: str, old_worker: str, old_startdate: str, old_enddate: str,
                          session: AsyncSession = Depends(get_async_session)):
    
    stmt_typevication_new = select(typevication.c.id).where(typevication.c.title == new_typevication)
    stmt_worker_new = select(worker.c.id).where(worker.c.fullname == new_worker)
    stmt_typevication_old = select(typevication.c.id).where(typevication.c.title == old_typevication)
    stmt_worker_old = select(worker.c.id).where(worker.c.fullname == old_worker)

    new_startdate = datetime.strptime(new_startdate, '%Y-%m-%d').date()
    new_enddate = datetime.strptime(new_enddate, '%Y-%m-%d').date()
    old_startdate = datetime.strptime(old_startdate, '%Y-%m-%d').date()
    old_enddate = datetime.strptime(old_enddate, '%Y-%m-%d').date()

    stmt_overlap_count = select(func.count()).where(
        and_(
            vicaion.c.worker_id == stmt_worker_new,
            or_(
                and_(vicaion.c.startdate <= new_startdate, vicaion.c.enddate >= new_startdate),
                and_(vicaion.c.startdate <= new_enddate, vicaion.c.enddate >= new_enddate),
                and_(vicaion.c.startdate >= new_startdate, vicaion.c.enddate <= new_enddate)
            )
        )
    )

    overlap_count = await session.execute(stmt_overlap_count)
    if overlap_count.scalar() > 0:
        return {'status': 'Error', 'message': f'Пересечение дат в {new_typevication} у {new_worker}.'}

    stmt = update(vicaion).values(typevication_id=stmt_typevication_new, worker_id=stmt_worker_new,
                                  startdate=new_startdate, enddate=new_enddate).\
                                    where(and_(vicaion.c.typevication_id == stmt_typevication_old, 
                                               vicaion.c.worker_id == stmt_worker_old, 
                                               vicaion.c.startdate == old_startdate, 
                                               vicaion.c.enddate == old_enddate))
    await session.execute(stmt)
    await session.commit()
    
    return {'status': 'OK'}