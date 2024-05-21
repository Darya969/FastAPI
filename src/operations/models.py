from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Date

metadata = MetaData()

typevication = Table(
    "typeVication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

post = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

worker = Table(
    "worker",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fullname", String, nullable=False),
    Column("login", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False),
)

dept = Table(
    "dept",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("worker_id", Integer, ForeignKey(worker.c.id)),
    Column("post_id", Integer, ForeignKey(post.c.id)),
)

vicaion = Table(
    "vication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("typevication_id", Integer, ForeignKey("typeVication.id")),
    Column("worker_id", Integer, ForeignKey(worker.c.id)),
    Column("startdate", Date, nullable=False),
    Column("enddate", Date, nullable=False),
)

