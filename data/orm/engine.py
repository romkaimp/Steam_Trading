import asyncio
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy import URL, create_engine, text, insert, String, JSON
from data.orm.config import settings
from typing import Annotated
import pickle

from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.orm import DeclarativeBase

async_engine = create_async_engine(settings.DATABASE_URL_asyncpg,
                                   echo_pool=True,
                                   pool_size=0,
                                   #max_overflow=50,
                                   pool_recycle=600,
                                   isolation_level="AUTOCOMMIT",
                                   connect_args={"timeout": 60})

async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

str_256 = Annotated[str, 256]
str_512 = Annotated[str, 512]
str_256_pk = Annotated[str_256, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    type_annotations_map = {
        str_256_pk: String(256),
        str_256: String(256),
        str_512: String(512),
    }

    def __repr__(self):
        cols = []
        for col in self.__table__.columns.keys():
            if str(col)[len(str(col))-4:len(str(col))]=="pckl":
                cols.append(f"{col}={pickle.loads(getattr(self, col)).shape}")
            elif str(col)[:3] == "image":
                cols.append(f"{col}=img")
            else:
                if getattr(self, col) is not None and type(getattr(self, col)) != int:
                    cols.append(f"{col}={getattr(self, col)[:10]}")
                else:
                    cols.append(f"{col}={getattr(self, col)}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"

    def __str__(self):
        cols = []
        for col in self.__table__.columns.keys():
            if str(col)[len(str(col)) - 4:len(str(col))] == "pckl":
                cols.append(f"{col}=pckl")
            else:
                cols.append(f"{col}={getattr(self, col)[:10]}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"


class Base2(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base2):
    pass


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base2.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    yield async_session()

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

