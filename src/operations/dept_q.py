from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_, or_, func
from database import get_async_session
from operations.models import worker, post, dept

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