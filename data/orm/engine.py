import asyncio
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy import URL, create_engine, text, insert, String, JSON
from data.orm.config import settings
from typing import Annotated
import pickle


async_engine = create_async_engine(settings.DATABASE_URL_asyncpg,
                                   echo=False,
                                   pool_size=5,
                                   max_overflow=10,
                                   pool_recycle=3600)


#sync_engine = create_engine(url=settings.DATABASE_URL_psycopg,
#                            echo=False,
#                            #pool_size=5,
#                            #max_overflow=10,
#                            #pool_recycle=3600
#)
#
#sync_engine_sqlite = create_engine(url=settings.DATABASE_URL_sqlite,
#                                   echo=True)


async def exe_query():
    async with async_engine.connect() as conn:
        a = await conn.execute(text("SELECT 1, 2, 3 union SELECT 4, 5, 6"))

        #print(f"{res.all()}")
#asyncio.run(exe_query())

# with sync_engine_sqlite.connect() as conn:
#     res = conn.execute(text("SELECT 1, 2, 3 union SELECT 4, 5, 6"))
#     print(f"{res.all()}")
#

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
                if getattr(self, col) is not None:
                    cols.append(f"{col}={getattr(self, col)[:10]}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"

    def __str__(self):
        cols = []
        for col in self.__table__.columns.keys():
            if str(col)[len(str(col)) - 4:len(str(col))] == "pckl":
                cols.append(f"{col}=pckl")
            else:
                cols.append(f"{col}={getattr(self, col)[:10]}")
        return f"<{self.__class__.__name__} {','.join(cols)}>"

if __name__ == '__main__':
    asyncio.run(exe_query())
