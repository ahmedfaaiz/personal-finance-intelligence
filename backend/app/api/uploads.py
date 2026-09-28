from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.ingestion import (
    MAX_FILE_SIZE_BYTES,
    OPTIONAL_COLUMNS,
    IngestionError,
    read_csv_bytes,
)

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.post("")
async def upload_csv(file: UploadFile = File(...)) -> dict:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported right now.")

    # Read one byte more than the limit so oversized files are detected safely.
    content = await file.read(MAX_FILE_SIZE_BYTES + 1)

    try:
        df = read_csv_bytes(content)
    except IngestionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "filename": filename,
        "rows_total": len(df),
        "columns": list(df.columns),
        "optional_columns_found": [col for col in OPTIONAL_COLUMNS if col in df.columns],
        "preview": df.head(5).to_dict(orient="records"),
    }