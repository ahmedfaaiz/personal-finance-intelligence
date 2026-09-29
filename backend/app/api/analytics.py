from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.stats import (
    get_category_breakdown,
    get_daily_trend,
    get_monthly_breakdown,
    get_summary,
    get_top_merchants,
)
from app.database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    return get_summary(db)


@router.get("/categories")
def categories(db: Session = Depends(get_db)) -> list[dict]:
    return get_category_breakdown(db)


@router.get("/monthly")
def monthly(db: Session = Depends(get_db)) -> list[dict]:
    return get_monthly_breakdown(db)


@router.get("/trends")
def trends(db: Session = Depends(get_db)) -> list[dict]:
    return get_daily_trend(db)


@router.get("/merchants")
def merchants(db: Session = Depends(get_db), limit: int = 10) -> list[dict]:
    return get_top_merchants(db, limit=limit)