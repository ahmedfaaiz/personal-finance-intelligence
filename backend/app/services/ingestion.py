import io

import pandas as pd

REQUIRED_COLUMNS = ["date", "description", "amount"]
OPTIONAL_COLUMNS = ["type", "category", "merchant", "payment_method"]
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_ROWS = 50_000


class IngestionError(Exception):
    """Raised when an uploaded file cannot be accepted."""


def read_csv_bytes(content: bytes) -> pd.DataFrame:
    """Validate raw CSV bytes and return them as a DataFrame of text values."""
    if not content.strip():
        raise IngestionError("The file is empty.")
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise IngestionError("The file is too large. The maximum size is 5 MB.")

    try:
        text = content.decode("utf-8-sig")  # handles Excel's CSV "BOM" marker too
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    try:
        # dtype=str keeps every value as text so cleaning (Phase 5) can inspect it.
        # keep_default_na=False keeps empty cells as "" instead of hiding them.
        df = pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        raise IngestionError(f"The file could not be read as a CSV: {error}") from error

    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise IngestionError(f"Missing required column(s): {', '.join(missing)}.")
    if df.empty:
        raise IngestionError("The file has a header row but no transactions.")
    if len(df) > MAX_ROWS:
        raise IngestionError(f"Too many rows. The maximum is {MAX_ROWS}.")

    return df