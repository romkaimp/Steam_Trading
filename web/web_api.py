from fastapi import FastAPI
from .prediction import router as rt

app = FastAPI(docs_url="/docs", openapi_url='/openapi.json', redoc_url=None)
app.include_router(rt)


