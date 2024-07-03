from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_, or_, func
from database import get_async_session
from operations.models import post, dept

dept_q = APIRouter(
    prefix="/dept",
    tags=["Dept"]
)

@dept_q.post('/create')
async def add_dept(title: str, worker_id: int, post_d: str, 
                   session: AsyncSession = Depends(get_async_session)):
    stmt_post_id = select(post.c.id).where(post.c.title == post_d)

    stmt_existing_worker = select(dept.c.id).where(dept.c.worker_id == worker_id)
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Сотрудник уже существует.'}

    if post_d == "руководитель" or post_d == "главный бухгалтер":
        stmt_post_count = select(func.count()).where(
            and_(dept.c.title == title, post.c.title == post_d)
        )
        post_count = await session.execute(stmt_post_count)
        if post_count.scalar() > 0:
            return {'status': 'Error', 'message': f'В "{title}" должность "{post_d}" уже занята.'}

    stmt = insert(dept).values(title=title, worker_id=worker_id, post_id=stmt_post_id)
    await session.execute(stmt)
    await session.commit()
    
    new_dept = select(dept).where(dept.c.title == title, dept.c.worker_id == worker_id, dept.c.post_id == stmt_post_id)
    insert_dept = await session.execute(new_dept)
    return {'status': 'OK', 'data': insert_dept.mappings().all()}

@dept_q.get("/search")
async def get_dept(dept_title: str, session: AsyncSession = Depends(get_async_session)):
    query = select(dept.c.id, dept.c.title, dept.c.worker_id, post.c.title).select_from(
        dept.join(post, post.c.id == dept.c.post_id)).where(dept.c.title == dept_title)
    result = await session.execute(query)
    return result.mappings().all()

@dept_q.post('/update')
async def update_dept(old_dept_id: int, new_title: str | None = None, worker_n: int | None = None, 
                      post_n: str | None = None, session: AsyncSession = Depends(get_async_session)):    
    if post_n == "руководитель" or post_n == "главный бухгалтер":
        stmt_post_count = select(func.count()).where(
            and_(dept.c.title == new_title, post.c.title == post_n)
        )
        post_count = await session.execute(stmt_post_count)
        if post_count.scalar() > 1:
            return {'status': 'Error', 'message': f'В "{new_title}" должность "{post_n}" уже занята.'}
    
    stmt_post_id_new = select(post.c.id).where(post.c.title == post_n)

    update_data = {}
    if new_title is not None:
        update_data['title'] = new_title
        stmt_dept_count = select(func.count()).where(
                and_(dept.c.title == new_title, or_(post.c.title == "руководитель", 
                                                    post.c.title == "главный бухгалтер")))
        dept_count = await session.execute(stmt_dept_count)
        if dept_count.scalar() > 0:
            return {'status': 'Error', 'message': f'В "{new_title}" должность уже занята.'}
    if worker_n is not None:
        update_data['worker_id'] = worker_n
    if post_n is not None:
        update_data['post_id'] = stmt_post_id_new

    if update_data:            
        stmt_update = (update(dept).where(dept.c.id == old_dept_id).values(**update_data).returning(dept))
        await session.execute(stmt_update)
        await session.commit()
    
    new_dept = select(dept).where(dept.c.id == old_dept_id)
    insert_dept = await session.execute(new_dept)
    return {'status': 'OK', 'data': insert_dept.mappings().all()}