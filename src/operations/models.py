from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, MetaData
from database import metadata

typevication = Table(
    "typeVication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    extend_existing=True
)

post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    extend_existing=True
)

worker = Table(
    "worker",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("surname", String, nullable=False),
    Column("name", String, nullable=False),
    Column("patronymic", String, nullable=False),
    Column("login", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False),
    extend_existing=True
)

dept = Table(
    "dept",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("worker_id", Integer, ForeignKey(worker.c.id)),
    Column("post_id", Integer, ForeignKey(post.c.id)),
    extend_existing=True
)

vicaion = Table(
    "vication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("typevication_id", Integer, ForeignKey("typeVication.id")),
    Column("worker_id", Integer, ForeignKey(worker.c.id)),
    Column("startdate", Date, nullable=False),
    Column("enddate", Date, nullable=False),
    extend_existing=True
)