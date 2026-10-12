from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CleaningLog, RejectedRow, Transaction, Upload

router = APIRouter(prefix="/api", tags=["data"])


@router.get("/transactions")
def list_transactions(limit: int = 100, db: Session = Depends(get_db)) -> list[dict]:
    limit = max(1, min(limit, 500))
    rows = (
        db.execute(
            select(Transaction)
            .order_by(Transaction.date.desc(), Transaction.id.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [
        {
            "id": t.id,
            "date": t.date.isoformat(),
            "merchant": t.merchant,
            "amount": t.amount,
            "type": t.type,
            "category": t.category,
            "category_source": t.category_source,
            "is_duplicate": t.is_duplicate,
        }
        for t in rows
    ]


@router.delete("/data")
def reset_data(db: Session = Depends(get_db)) -> dict:
    """Delete every stored upload, transaction and log. Used to start a clean demo."""
    deleted = db.query(Transaction).count()
    db.query(CleaningLog).delete()
    db.query(RejectedRow).delete()
    db.query(Transaction).delete()
    db.query(Upload).delete()
    db.commit()
    return {"deleted_transactions": deleted}