from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from database import get_async_session
from operations.models import post
from operations.schemas import PostCreate

post_q = APIRouter(
    prefix="/post",
    tags=["Post"]
)

@post_q.post('/create')
async def add_post(title: str, session: AsyncSession = Depends(get_async_session)):
    stmt_existing_worker = select(post.c.id).where(post.c.title.ilike(title))
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Такая должность "{title}" уже есть в базе данных.'}
    
    stmt = insert(post).values(title=title)
    result = await session.execute(stmt)
    await session.commit()

    new_type = select(post).where(post.c.title == title)
    insert_worker = await session.execute(new_type)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}

@post_q.get("/search")
async def get_post(session: AsyncSession = Depends(get_async_session)):
    query = select(post)
    result = await session.execute(query)
    return result.mappings().all()

@post_q.post('/update')
async def update_post(old_title: str, title: str, session: AsyncSession = Depends(get_async_session)):
    stmt_existing_worker = select(post.c.id).where(post.c.title.ilike(title))
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Такая должность "{title}" уже есть в базе данных.'}
    
    stmt =  update(post).values(title=title).where(post.c.title == old_title)
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}