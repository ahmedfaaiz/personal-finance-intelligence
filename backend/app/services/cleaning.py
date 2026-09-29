import re
from dataclasses import dataclass, field
from datetime import date, datetime

import pandas as pd

# ---- Merchant normalization -------------------------------------------------

# Very common Indian merchant patterns -> clean display name.
# This is a simple starting rule set; Phase 6 adds smarter categorization on top.
MERCHANT_PATTERNS: list[tuple[str, str]] = [
    (r"swiggy", "Swiggy"),
    (r"zomato", "Zomato"),
    (r"uber", "Uber"),
    (r"ola\b", "Ola"),
    (r"amazon", "Amazon"),
    (r"flipkart", "Flipkart"),
    (r"netflix", "Netflix"),
    (r"spotify", "Spotify"),
    (r"\bdmart\b", "DMart"),
    (r"salary", "Salary"),
]


def normalize_merchant(raw_description: str) -> str:
    """Turn a messy description like 'SWIGGY*ORDER123456' into 'Swiggy'."""
    text = raw_description.strip()
    lowered = text.lower()
    for pattern, clean_name in MERCHANT_PATTERNS:
        if re.search(pattern, lowered):
            return clean_name
    # Fallback: strip trailing order/reference numbers and extra symbols.
    cleaned = re.sub(r"[*#].*$", "", text)          # drop "*ORDER123" style suffixes
    cleaned = re.sub(r"\s+\d{4,}$", "", cleaned)     # drop long trailing numbers
    cleaned = re.sub(r"[_\-]+", " ", cleaned).strip()
    return cleaned.title() if cleaned else "Unknown"


# ---- Row-level parsing -------------------------------------------------------

def parse_date(raw_value: str) -> date | None:
    text = raw_value.strip()
    if not text:
        return None
    # Try the formats we expect from CSV exports; add more here if needed.
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_amount(raw_value: str) -> float | None:
    text = raw_value.strip().replace(",", "").replace("₹", "").replace("$", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def infer_type(raw_type: str, amount: float) -> str:
    text = raw_type.strip().lower()
    if text in ("income", "credit", "in"):
        return "income"
    if text in ("expense", "debit", "out"):
        return "expense"
    # No usable type given: fall back to the sign of the amount.
    return "income" if amount > 0 else "expense"


# ---- Result containers -------------------------------------------------------

@dataclass
class CleaningLogEntry:
    row_number: int
    field: str
    action: str
    before_value: str | None
    after_value: str | None


@dataclass
class RejectedRowEntry:
    row_number: int
    raw_data: str
    reason: str


@dataclass
class CleanedTransaction:
    row_number: int
    date: date
    description_raw: str
    merchant: str
    amount: float
    type: str
    payment_method: str | None
    is_duplicate: bool = False


@dataclass
class CleaningResult:
    accepted: list[CleanedTransaction] = field(default_factory=list)
    rejected: list[RejectedRowEntry] = field(default_factory=list)
    logs: list[CleaningLogEntry] = field(default_factory=list)

    @property
    def rows_total(self) -> int:
        return len(self.accepted) + len(self.rejected)


def clean_dataframe(df: pd.DataFrame) -> CleaningResult:
    result = CleaningResult()
    seen_keys: set[tuple[date, str, float]] = set()

    for position, row in df.iterrows():
        row_number = int(position) + 2  # +1 for 0-index, +1 for the header row
        raw_dict = row.to_dict()

        raw_date = str(row.get("date", ""))
        raw_description = str(row.get("description", ""))
        raw_amount = str(row.get("amount", ""))
        raw_type = str(row.get("type", ""))
        raw_payment_method = str(row.get("payment_method", "")).strip() or None

        # --- Required field: description ---
        if not raw_description.strip():
            result.rejected.append(
                RejectedRowEntry(row_number, str(raw_dict), "Missing description.")
            )
            continue

        # --- Required field: date ---
        parsed_date = parse_date(raw_date)
        if parsed_date is None:
            result.rejected.append(
                RejectedRowEntry(row_number, str(raw_dict), f"Invalid or unrecognized date: '{raw_date}'.")
            )
            continue

        # --- Required field: amount ---
        parsed_amount = parse_amount(raw_amount)
        if parsed_amount is None:
            result.rejected.append(
                RejectedRowEntry(row_number, str(raw_dict), f"Invalid or non-numeric amount: '{raw_amount}'.")
            )
            continue
        if parsed_amount == 0:
            result.rejected.append(
                RejectedRowEntry(row_number, str(raw_dict), "Amount is zero.")
            )
            continue

        # --- Normalize type (log if we had to infer it) ---
        txn_type = infer_type(raw_type, parsed_amount)
        if not raw_type.strip():
            result.logs.append(
                CleaningLogEntry(row_number, "type", "inferred_from_amount_sign", None, txn_type)
            )

        # --- Normalize merchant ---
        clean_merchant = normalize_merchant(raw_description)
        if clean_merchant.lower() != raw_description.strip().lower():
            result.logs.append(
                CleaningLogEntry(row_number, "merchant", "normalized", raw_description, clean_merchant)
            )

        abs_amount = abs(parsed_amount)

        # --- Duplicate detection (same date + merchant + amount) ---
        dup_key = (parsed_date, clean_merchant.lower(), abs_amount)
        is_duplicate = dup_key in seen_keys
        if is_duplicate:
            result.logs.append(
                CleaningLogEntry(row_number, "row", "flagged_duplicate", None, str(dup_key))
            )
        else:
            seen_keys.add(dup_key)

        result.accepted.append(
            CleanedTransaction(
                row_number=row_number,
                date=parsed_date,
                description_raw=raw_description.strip(),
                merchant=clean_merchant,
                amount=abs_amount,
                type=txn_type,
                payment_method=raw_payment_method,
                is_duplicate=is_duplicate,
            )
        )

    return result