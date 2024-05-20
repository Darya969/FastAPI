from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Date, Boolean
from datetime import datetime

metadata = MetaData()

role = Table(
    "role",
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

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("login", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("email", String, nullable=False),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("date_reg", TIMESTAMP, default=datetime.utcnow),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

dept = Table(
    "dept",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("role_id", Integer, ForeignKey(role.c.id)),
)

vicaion = Table(
    "vication",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("typevication_id", Integer, ForeignKey("typeVication.id")),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("startdate", Date, nullable=False),
    Column("enddate", Date, nullable=False),
)