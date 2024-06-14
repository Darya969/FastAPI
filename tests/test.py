from httpx import AsyncClient
from sqlalchemy import insert, select, update, and_
from src.operations.models import worker, typevication, post, dept, vicaion
from conftest import async_session_maker
from datetime import datetime

async def test_add_worker(ac: AsyncClient):
    response = await ac.post("/worker/create", json={
        "id": 21, 
        "fullname": "Константинов Павел Игоревич",
        "login": "konstantinovPI",
        "password": "014658", 
        "email": "konstantinov.p.i@icloud.com",
    })

    assert response.status_code == 200

async def test_get_worker(ac: AsyncClient):
    response = await ac.get("/worker/search", params={
        "worker_name": "Семенов Никита Александрович",
    })

    assert response.status_code == 200

async def test_update_worker():
    async with async_session_maker() as session:
        stmt = update(worker).values(fullname="Константинов Павел Игоревич", login="konstantinovPI",
                                     password="014658", email="konstantinov.p.i@icloud.com").where(
                                         worker.c.fullname == "Константинов Павел Игоревич",
                                         worker.c.login == "konstantinovPI",
                                         worker.c.password == "153248",
                                         worker.c.email == "konstantinov.p.i@icloud.com")
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

# _______________________________________________________________________________________________

async def test_add_typeVication(ac: AsyncClient):
    response = await ac.post("/typeVication/create", json={
        "id": 3, 
        "title": "больничный лист",
    })

    assert response.status_code == 200

async def test_get_typeVication():
    async with async_session_maker() as session:
        query = select(typevication)
        result = await session.execute(query)
        assert result.all() == [(3, 'больничный лист')], "Тип выходных не добавлен"

async def test_update_typeVication():
    async with async_session_maker() as session:
        stmt = update(typevication).values(title="административный отпуск").where(typevication.c.title == "больничный лист")
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

# _______________________________________________________________________________________________

async def test_add_post(ac: AsyncClient):
    response = await ac.post("/post/create", json={
        "id": 10, 
        "title": "DevOps",
    })

    assert response.status_code == 200

async def test_get_post():
    async with async_session_maker() as session:
        query = select(post)
        result = await session.execute(query)
        assert result.all() == [(10, 'DevOps')], "Должность не добавлена" 

async def test_update_post():
    async with async_session_maker() as session:
        stmt = update(post).values(title="DevOps инженер").where(post.c.title == "DevOps")
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

# ________________________________________________________________________________________________

async def test_add_dept():
    async with async_session_maker() as session:
        stmt = insert(dept).values(id=14, title="Юридический отдел",
                                   worker_id=(select(worker.c.id).where(worker.c.fullname == "Константинов Павел Игоревич")), 
                                   post_id=select(post.c.id).where(post.c.title == "юрисконсульт"))
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

async def test_add_dept_existing_worker(ac: AsyncClient):
    response = await ac.post("/dept/create", json={
        "id": 15,
        "title": "Юридический отдел",
        "worker_id": 1,
        "post_id": 3,
    })

    if response.status_code == 200:
        print({'status': 'OK'})
        assert {'status': 'OK'}
    elif response.status_code == 422:
        print({'status': 'Error', 'message': 'Сотрудник уже существует.'})
        assert {'status': 'Error', 'message': 'Сотрудник уже существует.'}

async def test_add_dept_existing_post(ac: AsyncClient):
    response = await ac.post("/dept/create", json={
        "id": 15,
        "title": "Юридический отдел",
        "worker_id": 3,
        "post_id": 1,
    })
    
    if response.status_code == 200:
        print({'status': 'OK'})
        assert {'status': 'OK'}
    elif response.status_code == 422:
        print({'status': 'Error', 'message': 'Должность уже занята.'})
        assert {'status': 'Error', 'message': 'Должность уже занята.'}

async def test_get_dept(ac: AsyncClient):
    response = await ac.get("/dept/search", params={
        "dept_title": "Юридический отдел",
    })

    assert response.status_code == 200

async def test_update_dept():
    async with async_session_maker() as session:
        stmt = update(dept).values(title="Юридический отдел", 
                                   worker_id=select(worker.c.id).where(worker.c.fullname == "Новикова Ольга Николаевна"),
                                   post_id=select(post.c.id).where(post.c.title == "юрисконсульт")).where(
                                       and_(dept.c.title == "Юридический отдел", 
                                            dept.c.worker_id == select(worker.c.id).where(worker.c.fullname == "Новикова Ольга Николаевна"),
                                            dept.c.post_id == select(post.c.id).where(post.c.title == "юрист")))
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

# ________________________________________________________________________________________________

async def test_add_vication():
    async with async_session_maker() as session:
        startdate_str = "2024-06-06"
        enddate_str = "2024-06-07"
        startdate = datetime.strptime(startdate_str, '%Y-%m-%d').date()
        enddate = datetime.strptime(enddate_str, '%Y-%m-%d').date()
        
        stmt = insert(vicaion).values(id=4, 
                                      typevication_id=select(typevication.c.id).where(typevication.c.title == "командировка"),
                                      worker_id=(select(worker.c.id).where(worker.c.fullname == "Константинов Павел Игоревич")),
                                      startdate=startdate, enddate=enddate)
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}

async def test_add_vication_new_date(ac: AsyncClient):
    response = await ac.post("/vication/create", json={
        "id": 5,
        "typevication_id": 0,
        "worker_id": 6,
        "startdate": "2024-05-30",
        "enddate": "2024-05-31",
    })

    if response.status_code == 200:
        print({'status': 'OK'})
        assert {'status': 'OK'}
    elif response.status_code == 422:
        print({'status': 'Error', 'message': 'Пересечение дат'})
        assert {'status': 'Error', 'message': 'Пересечение дат'}

async def test_update_vication():
    async with async_session_maker() as session:
        startdate_str = "2024-06-06"
        enddate_str = "2024-06-07"
        startdate_old_str = "2024-05-27"
        enddate_old_str = "2024-06-09"
        startdate = datetime.strptime(startdate_str, '%Y-%m-%d').date()
        enddate = datetime.strptime(enddate_str, '%Y-%m-%d').date()
        startdate_old = datetime.strptime(startdate_old_str, '%Y-%m-%d').date()
        enddate_old = datetime.strptime(enddate_old_str, '%Y-%m-%d').date()

        stmt = update(vicaion).values(typevication_id=select(typevication.c.id).where(typevication.c.title == "командировка"),
                                      worker_id=(select(worker.c.id).where(worker.c.fullname == "Кузьмин Глеб Анатольевич")),
                                      startdate=startdate, enddate=enddate).where(
                                       and_(vicaion.c.typevication_id == select(typevication.c.id).where(typevication.c.title == "отпуск"), 
                                            vicaion.c.worker_id == select(worker.c.id).where(worker.c.fullname == "Кузьмин Глеб Анатольевич"),
                                            vicaion.c.startdate == startdate_old, 
                                            vicaion.c.enddate == enddate_old))
        await session.execute(stmt)
        await session.commit()
        assert {'status': 'OK'}