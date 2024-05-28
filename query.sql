SELECT * FROM worker;

INSERT INTO worker 
VALUES (17, 'Ковалев Алексей Игоревич', 'kovalevAI', '147741', 'kovalev.a.i@yandex.ru'),
		(18, 'Попова Елена Владимировна', 'popovaEV', '963369', 'popova.e.v@gmail.com'),
		(19, 'Семенов Никита Александрович', 'semenovNA', '258852', 'semenov.n.a@rambler.ru'),
		(20, 'Иванова Виктория Дмитриевна', 'ivanovaVD', '258741', 'ivanova.v.d@gmail.com');

WITH selected_data AS (
    SELECT * FROM worker
)
UPDATE worker
SET fullname = 'Кузьмин Глеб Анатольевич'
FROM selected_data
WHERE worker.fullname = 'test';

SELECT * FROM dept;

INSERT INTO dept VALUES (1, 'Юридический отдел', 1, 1);

SELECT dept.id, dept.title, worker.fullname, post.title
FROM dept
JOIN worker ON worker.id = dept.worker_id
JOIN post ON post.id = dept.post_id
WHERE dept.title = 'Юридический отдел';

INSERT INTO dept(id, title, worker_id, post_id)
VALUES (2, 'Юридический отдел', 
		(SELECT id FROM worker WHERE fullname='Новикова Ольга Николаевна'),
		(SELECT id FROM post WHERE title='юрист'))
		
SELECT dept.id, dept.title, worker.fullname, post.title
FROM dept
JOIN worker ON worker.id = dept.worker_id
JOIN post ON post.id = dept.post_id
WHERE dept.title = 'Бухгалтерия' and
worker.fullname = 'Смирнова Екатерина Сергеевна';

UPDATE dept
SET worker_id = (SELECT id FROM worker WHERE fullname = 'Петров Александр Иванович'),
	post_id = (SELECT id FROM post WHERE title = 'юрисконсульт')
WHERE worker_id = (SELECT id FROM worker WHERE fullname = 'Кузьмин Глеб Анатольевич')
	AND post_id = (SELECT id FROM post WHERE title = 'руководитель');
	
DELETE FROM dept WHERE id=13;

SELECT dept.id, dept.title, worker.fullname, post.title
FROM dept
JOIN worker ON worker.id = dept.worker_id
JOIN post ON post.id = dept.post_id
WHERE dept.title = 'IT отдел' and 
(post.title = 'системный администратор' or post.title = 'руководитель')

SELECT vication.id, public."typeVication".title, worker.fullname, vication.startdate,
	vication.enddate
FROM vication
JOIN public."typeVication" ON public."typeVication".id = vication.typevication_id
JOIN worker ON worker.id = vication.worker_id;

INSERT INTO vication(id, typevication_id, worker_id, startdate, enddate)
VALUES (1,
		(SELECT id FROM public."typeVication" WHERE title='отпуск'),
		(SELECT id FROM worker WHERE fullname='Смирнова Екатерина Сергеевна'),
	   '2024-05-27', '2024-06-02');