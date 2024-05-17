from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Date
from datetime import datetime

metadata = MetaData()

roles = Table(
    "roles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

typevication = Table(
    "typeVication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
)

workers = Table(
    "workers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("login", String, nullable=False),
    Column("password", String, nullable=False),
    Column("email", String, nullable=False),
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("date_reg", TIMESTAMP, default=datetime.utcnow),
)

depts = Table(
    "depts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("worker_id", Integer, ForeignKey("workers.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)

vicaions = Table(
    "vications",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("typevication_id", Integer, ForeignKey("typeVication.id")),
    Column("workers_id", Integer, ForeignKey("workers.id")),
    Column("startdate", Date, nullable=False),
    Column("enddate", Date, nullable=False),
)