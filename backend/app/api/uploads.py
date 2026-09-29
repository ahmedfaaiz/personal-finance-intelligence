from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CleaningLog, RejectedRow, Transaction, Upload
from app.services.cleaning import clean_dataframe
from app.services.ingestion import MAX_FILE_SIZE_BYTES, IngestionError, read_csv_bytes
from app.services.categorization import categorize_rule_based
from app.services.ml_categorizer import ml_categorizer
router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported right now.")

    content = await file.read(MAX_FILE_SIZE_BYTES + 1)

    try:
        df = read_csv_bytes(content)
    except IngestionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    cleaning_result = clean_dataframe(df)

    # Create the upload record first, so we can attach transactions/rejections to it.
    upload = Upload(
        filename=filename,
        rows_total=cleaning_result.rows_total,
        rows_accepted=len(cleaning_result.accepted),
        rows_rejected=len(cleaning_result.rejected),
    )
    db.add(upload)
    db.flush()  # assigns upload.id without fully committing yet

    for txn in cleaning_result.accepted:
        rule_match = categorize_rule_based(txn.merchant, txn.description_raw)
        if rule_match:
            category, category_source = rule_match.category, rule_match.source
        elif txn.type == "income":
            category, category_source = "Salary", "rule"
        else:
            ml_match = ml_categorizer.predict(txn.merchant, txn.description_raw)
            category, category_source = ml_match.category, ml_match.source
        db.add(
            Transaction(
                upload_id=upload.id,
                date=txn.date,
                description_raw=txn.description_raw,
                merchant=txn.merchant,
                amount=txn.amount,
                type=txn.type,
                category=category,
                category_source=category_source,
                payment_method=txn.payment_method,
                is_duplicate=txn.is_duplicate,
            )
        )

    for rejected in cleaning_result.rejected:
        db.add(
            RejectedRow(
                upload_id=upload.id,
                row_number=rejected.row_number,
                raw_data=rejected.raw_data,
                reason=rejected.reason,
            )
        )

    for log_entry in cleaning_result.logs:
        db.add(
            CleaningLog(
                upload_id=upload.id,
                row_number=log_entry.row_number,
                field=log_entry.field,
                action=log_entry.action,
                before_value=log_entry.before_value,
                after_value=log_entry.after_value,
            )
        )

    db.commit()

    return {
        "upload_id": upload.id,
        "filename": filename,
        "rows_total": cleaning_result.rows_total,
        "rows_accepted": len(cleaning_result.accepted),
        "rows_rejected": len(cleaning_result.rejected),
        "duplicates_flagged": sum(1 for t in cleaning_result.accepted if t.is_duplicate),
        "fixes_applied": len(cleaning_result.logs),
        "rejected_rows": [
            {"row_number": r.row_number, "reason": r.reason} for r in cleaning_result.rejected
        ],
    }