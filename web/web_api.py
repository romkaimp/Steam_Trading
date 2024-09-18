from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .prediction import router as rt
from web.users import router as rt2

app = FastAPI(docs_url="/docs", openapi_url='/openapi.json', redoc_url=None)
app.include_router(rt)
app.include_router(rt2)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


