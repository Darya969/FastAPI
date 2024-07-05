from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from database import get_async_session
from operations.models import typevication
from operations.schemas import TypeCreate

typeVication = APIRouter(
    prefix="/typeVication",
    tags=["Type vication"]
)

@typeVication.post('/create')
async def add_typeVication(new_title: str, session: AsyncSession = Depends(get_async_session)):
    stmt_existing_worker = select(typevication.c.id).where(typevication.c.title.ilike(new_title))
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Тип отсутствия "{new_title}" уже есть в базе данных.'}
        
    stmt = insert(typevication).values(title=new_title)
    await session.execute(stmt)
    await session.commit()

    new_type = select(typevication).where(typevication.c.title == new_title)
    insert_worker = await session.execute(new_type)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}

@typeVication.get("/search")
async def get_typeVication(session: AsyncSession = Depends(get_async_session)):
    query = select(typevication)
    result = await session.execute(query)
    return result.mappings().all()

@typeVication.post('/update')
async def update_typeVication(old_type_id: int, new_title: str, session: AsyncSession = Depends(get_async_session)):
    stmt_existing_worker = select(typevication.c.id).where(typevication.c.title.ilike(new_title))
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Тип отсутствия "{new_title}" уже есть в базе данных.'}
    
    stmt =  update(typevication).values(title=new_title).where(typevication.c.id == old_type_id)
    await session.execute(stmt)
    await session.commit()
    return {'status': 'OK'}