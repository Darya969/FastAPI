from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_, or_, func
from database import get_async_session
from operations.models import worker, typevication, vicaion
from datetime import datetime

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