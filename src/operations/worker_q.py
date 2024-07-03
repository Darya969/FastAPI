from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, or_, and_, alias
from sqlalchemy.orm import aliased
from database import get_async_session
from operations.models import worker, dept, post

worker_q = APIRouter(
    prefix="/worker",
    tags=["Worker"]
)

@worker_q.post("/create")
async def add_worker(surname: str, name: str, patronymic: str, login: str, password: str, email: str,
                     session: AsyncSession = Depends(get_async_session)):
    stmt_existing_worker = select(worker.c.id).where(worker.c.login == login)
    existing_worker = await session.execute(stmt_existing_worker)
    existing_worker = existing_worker.scalar()

    if existing_worker:
        return {'error': f'Сотрудник уже существует.'}

    stmt = insert(worker).values(surname=surname, name=name, patronymic=patronymic, login=login, 
                                 password=password, email=email)
    result = await session.execute(stmt)
    await session.commit()

    new_worker = select(worker).where(worker.c.surname == surname, worker.c.name == name, 
                                      worker.c.patronymic == patronymic, worker.c.email == email)
    insert_worker = await session.execute(new_worker)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}

@worker_q.get("/search")
async def get_worker(surname: str | None = None, name: str | None = None, 
                     patronymic: str | None = None, email: str | None = None, 
                     session: AsyncSession = Depends(get_async_session)):
    
    # Создаем псевдонимы для таблиц
    w = aliased(worker)
    d = aliased(dept)
    d1 = aliased(dept)
    p1 = aliased(dept)

    # Создаем подзапросы
    subquery_worker = select(d1.c.worker_id).where(d1.c.title == d.c.title).where(d1.c.post_id == 1).scalar_subquery()

    update_data = []
    if surname is not None:
        update_data.append(w.c.surname.ilike(surname))
    if name is not None:
        update_data.append(w.c.name.ilike(name))
    if patronymic is not None:
        update_data.append(w.c.patronymic.ilike(patronymic))
    if email is not None:
        update_data.append(w.c.email.ilike(email))


    # Создаем основной запрос
    query = select(
        w.c.id,
        w.c.surname,
        w.c.name,
        w.c.patronymic,
        w.c.login,
        w.c.password,
        w.c.email,
        d.c.title.label('dept_title'),
        select(post.c.title).where(post.c.id == 1).subquery(),
        subquery_worker.label('worker')
    ).select_from(w).outerjoin(d, d.c.worker_id == w.c.id).where(and_(*update_data))

    # d1 = alias(dept)

    # surname_w = select(worker.c.surname).\
    #     select_from(dept.join(worker, dept.c.worker_id == worker.c.id, isouter=True)).\
    #     where(and_(dept.c.post_id == 1, dept.c.title == dept.c.title)).scalar_subquery()

    # query = select(worker.c.id, worker.c.surname, worker.c.name, worker.c.patronymic, worker.c.login,
    #            worker.c.password, worker.c.email, dept.c.title,
    #            select(post.c.title).where(post.c.id == 1),
    #            select(worker.c.surname).select_from(dept.join(worker, and_(dept.c.worker_id == worker.c.id,
    #                                                                        dept.c.post_id == 1,
    #                                                                        dept.c.title == dept.c.title))),
    #            select(worker.c.name).select_from(dept.join(worker, and_(dept.c.worker_id == worker.c.id,
    #                                                                     dept.c.post_id == 1,
    #                                                                     dept.c.title == dept.c.title))),
    #            select(worker.c.patronymic).select_from(dept.join(worker, and_(dept.c.worker_id == worker.c.id,
    #                                                                           dept.c.post_id == 1,
    #                                                                           dept.c.title == dept.c.title)))).select_from(
    #                worker.join(dept, dept.c.worker_id == worker.c.id).join(post, post.c.id == dept.c.post_id, isouter=True)
    #            ).where(and_(or_(*update_data)), post.c.id == 1 if post.c.id == 1 else True)

    # query = select(worker.c.id, worker.c.surname, worker.c.name, worker.c.patronymic, worker.c.login, 
    #                worker.c.password, worker.c.email, dept.c.title, 
    #                select(post.c.title).where(post.c.id == 1).subquery(),
    #                select(worker.c.surname).\
    #                 select_from(dept.join(worker, dept.c.worker_id == worker.c.id, isouter=True)).\
    #                     where(and_(dept.c.post_id == 1, d1.c.title == dept.c.title)).correlate(dept).subquery()).\
    #                         where(and_(*update_data, post.c.id == 1 if post.c.id == 1 else True))
                    #                                                             select_from(
                    #    worker.join(dept, dept.c.worker_id == worker.c.id).\
                    #     join(post, post.c.id == dept.c.post_id, isouter=True)).\
                        # where(and_(or_(*update_data)), post.c.id == 1 if post.c.id == 1 else True)
    
    # query = select(dept.c.id, dept.c.title, dept.c.worker_id, post.c.title).select_from(
    #     dept.join(post, post.c.id == dept.c.post_id)).where(dept.c.title == dept_title)

    # query = select(worker).where(or_(*update_data))
    result = await session.execute(query)
    return result.mappings().all()

@worker_q.post("/update")
async def update_worker(old_worker_id: int, surname: str | None = None, name: str | None = None, 
                        patronymic: str | None = None, login: str | None = None,  passw: str | None = None, 
                        email: str | None = None, session: AsyncSession = Depends(get_async_session)):
    update_data = {}
    if surname is not None:
        update_data['surname'] = surname
    if name is not None:
        update_data['name'] = name
    if patronymic is not None:
        update_data['patronymic'] = patronymic
    if login is not None:
        update_data['login'] = login
    if passw is not None:
        update_data['passw'] = passw
    if email is not None:
        update_data['email'] = email

    if update_data:
        stmt = (update(worker).where(worker.c.id == old_worker_id).values(**update_data).returning(worker))
        result = await session.execute(stmt)
        await session.commit()

    update_worker = select(worker).where(worker.c.id == old_worker_id)
    insert_worker = await session.execute(update_worker)
    return {'status': 'OK', 'data': insert_worker.mappings().all()}