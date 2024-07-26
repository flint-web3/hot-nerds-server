#!.venv/bin/python
import sqlite3
import enum
import dotenv
from datetime import datetime as dt
from sqlalchemy import Column, Enum, Integer, String, Boolean, Float, Table, DateTime, ForeignKey, MetaData, insert, create_engine

db_name = dotenv.get_key(dotenv.find_dotenv(), "db_name")

conn = sqlite3.connect(db_name) # type: ignore
conn.close()

enigne = create_engine(f"sqlite:///{db_name}", echo=True)
meta = MetaData()

user_table = Table(
    "user",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("account_name", String, unique=True, index=True),
    Column("private_key", String, nullable=True, default=None),
)


class QuizTypeEnum(enum.Enum):
    daily = 1
    armageddon = 2
    event = 3


quiz_table = Table(
    "quiz",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=True),
    Column("price", Float),
    Column("due", DateTime),
    Column("type", Enum(QuizTypeEnum), default=QuizTypeEnum.daily),
    Column("is_finished", Boolean, default=False),
)

user_score_table = Table(
    "user_score",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("score", Integer, default=0),
    Column("quiz_id", Integer, ForeignKey("quiz.id")),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("shard", String, nullable=True, default=None),
)

meta.create_all(enigne)

stmt = (
    insert(quiz_table).
    values(name="Event Quiz", price=5.0, due=dt.fromtimestamp(1722927600), type=QuizTypeEnum.event)
)
with enigne.connect() as conn: # type: ignore
    result = conn.execute(statement=stmt) # type: ignore
    conn.commit()

stmt = (
    insert(quiz_table).
    values(name="Daily Quiz", price=0.5, due=dt.fromtimestamp(1722927600), type=QuizTypeEnum.daily)
)
with enigne.connect() as conn: # type: ignore
    result = conn.execute(statement=stmt) # type: ignore
    conn.commit()
