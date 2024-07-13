from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_, or_, func, cast, Date
from database import get_async_session
from operations.models import worker, typevication, vicaion
from datetime import datetime
import calendar

vication_q = APIRouter(
    prefix="/vication",
    tags=["Vication"]
)

@vication_q.post("/create")
async def add_vication(new_typevication: str, new_worker_id: int, new_startdate: str, new_enddate: str,
                   session: AsyncSession = Depends(get_async_session)):
    
    stmt_typevication_id = select(typevication.c.id).where(typevication.c.title == new_typevication)

    try:        
        new_startdate_dt = datetime.strptime(new_startdate, '%Y-%m-%d').date()
        new_enddate_dt = datetime.strptime(new_enddate, '%Y-%m-%d').date()

        calendar.monthrange(new_startdate_dt.year, new_startdate_dt.month)
        calendar.monthrange(new_enddate_dt.year, new_enddate_dt.month)
    except (ValueError, calendar.IllegalMonthError):
        return {'status': 'Error', 'message': 'Некорректная дата. Не является допустимым днем.'}

    stmt_overlap_count = select(func.count()).where(
        and_(
            vicaion.c.worker_id == new_worker_id,
            or_(
                and_(vicaion.c.startdate <= new_startdate_dt, vicaion.c.enddate >= new_startdate_dt),
                and_(vicaion.c.startdate <= new_enddate_dt, vicaion.c.enddate >= new_enddate_dt),
                and_(vicaion.c.startdate >= new_startdate_dt, vicaion.c.enddate <= new_enddate_dt)
            )
        )
    )

    overlap_count = await session.execute(stmt_overlap_count)
    if overlap_count.scalar() > 0:
        return {'status': 'Error', 'message': f'Пересечение дат в {new_typevication} у сотрудника.'}

    stmt = insert(vicaion).values(typevication_id=stmt_typevication_id, worker_id=new_worker_id, 
                                  startdate=new_startdate_dt, enddate=new_enddate_dt)
    await session.execute(stmt)
    await session.commit()
    
    new_vication = select(vicaion).where(vicaion.c.typevication_id == stmt_typevication_id, vicaion.c.worker_id == new_worker_id, 
                                     vicaion.c.startdate == new_startdate_dt, vicaion.c.enddate == new_enddate_dt)
    insert_vication = await session.execute(new_vication)
    return {'status': 'OK', 'data': insert_vication.mappings().all()}

@vication_q.get("/search")
async def get_vication(surname: str, name: str, patronymic: str, session: AsyncSession = Depends(get_async_session)):
    query = select(vicaion.c.id, typevication.c.title, worker.c.surname, worker.c.name, worker.c.patronymic,
                   vicaion.c.startdate, vicaion.c.enddate).select_from(
        vicaion.join(typevication, typevication.c.id == vicaion.c.typevication_id)
        .join(worker, worker.c.id == vicaion.c.worker_id)).\
        where(and_(worker.c.surname == surname, worker.c.name == name, worker.c.patronymic == patronymic))
    result = await session.execute(query)
    return result.mappings().all()

@vication_q.post("/update")
async def update_vication(old_vication_id: int, new_typevication: str | None = None, new_worker_id: int | None = None, 
                          new_startdate: str | None = None, new_enddate: str | None = None,
                          session: AsyncSession = Depends(get_async_session)):
    update_data = {}
    
    if new_typevication is not None:
        stmt_typevication_new = select(typevication.c.id).where(typevication.c.title == new_typevication)
        update_data['typevication_id'] = stmt_typevication_new.scalar_subquery()
    if new_worker_id is not None:
        update_data['worker_id'] = new_worker_id
    if new_startdate is not None:
        try:        
            new_startdate_dt = datetime.strptime(new_startdate, '%Y-%m-%d').date()
            calendar.monthrange(new_startdate_dt.year, new_startdate_dt.month)
            update_data['startdate'] = new_startdate_dt
        except (ValueError, calendar.IllegalMonthError):
            return {'status': 'Error', 'message': 'Некорректная дата. Не является допустимым днем.'}   
    if new_enddate is not None:
        try:
            new_enddate_dt = datetime.strptime(new_enddate, '%Y-%m-%d').date()
            calendar.monthrange(new_enddate_dt.year, new_enddate_dt.month)
            update_data['enddate'] = new_enddate_dt
        except (ValueError, calendar.IllegalMonthError):
            return {'status': 'Error', 'message': 'Некорректная дата. Не является допустимым днем.'}
    if 'startdate' in update_data and 'enddate' in update_data:
        stmt_overlap_count = select(func.count()).where(
            and_(
                vicaion.c.worker_id == new_worker_id,
                or_(
                    and_(vicaion.c.startdate <= update_data['startdate'], vicaion.c.enddate >= update_data['startdate']),
                    and_(vicaion.c.startdate <= update_data['enddate'], vicaion.c.enddate >= update_data['enddate']),
                    and_(vicaion.c.startdate >= update_data['startdate'], vicaion.c.enddate <= update_data['enddate'])
                )
            )
        )

        overlap_count = await session.execute(stmt_overlap_count)
        if overlap_count.scalar() > 0:
            return {'status': 'Error', 'message': f'Пересечение дат в {new_typevication} у сотрудника.'}

    if update_data:            
        stmt_update = (update(vicaion).where(vicaion.c.id == old_vication_id).values(update_data).returning(vicaion))
        result = await session.execute(stmt_update)
        await session.commit()
    
    new_vication = select(vicaion).where(vicaion.c.id == old_vication_id)
    insert_vication = await session.execute(new_vication)
    return {'status': 'OK', 'data': insert_vication.mappings().all()}
