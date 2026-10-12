from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import analytics, chat, data, uploads
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create tables on startup
    yield


app = FastAPI(title="Personal Finance Intelligence API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router)
app.include_router(analytics.router)
app.include_router(chat.router)

app.include_router(data.router)
@app.get("/api/health")
def health_check() -> dict:
    return {"status": "ok"}


# This must stay at the very bottom, so it doesn't block the /api routes above.
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")