from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .prediction import router as rt
from web.users import router as rt2
from contextlib import asynccontextmanager
from data.orm.engine import User, create_db_and_tables

import data.fake_data.fake_orm as fkorm
from data.parser.parser import list_names_images

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    #fkorm.delete_all()
    #k = await list_names_images(5)
    #print(k)
    #fkorm.insert_all(k)
    await create_db_and_tables()
    yield

app = FastAPI(docs_url="/docs", openapi_url='/openapi.json', redoc_url=None, lifespan=lifespan)
app.include_router(rt)
app.include_router(rt2)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://127.0.0.1:5173",
    "https://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


