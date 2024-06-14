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