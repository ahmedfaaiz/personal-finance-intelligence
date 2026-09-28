from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import uploads
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create tables on startup
    yield


app = FastAPI(title="Personal Finance Intelligence API", lifespan=lifespan)
app.include_router(uploads.router)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}