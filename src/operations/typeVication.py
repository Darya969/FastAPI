from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from database import get_async_session
from operations.models import typevication
from operations.schemas import TypeCreate

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