from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.llm_client import generate_text
from app.analytics.stats import (
    get_category_breakdown,
    get_monthly_breakdown,
    get_summary,
    get_top_merchants,
)
from app.database import get_db

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str


def build_financial_context(db: Session) -> str:
    """Gather the user's real financial facts as plain text for the AI to read."""
    summary = get_summary(db)
    categories = get_category_breakdown(db)
    monthly = get_monthly_breakdown(db)
    merchants = get_top_merchants(db, limit=5)

    lines = [
        "=== USER'S ACTUAL FINANCIAL DATA ===",
        f"Total Income: ₹{summary['total_income']}",
        f"Total Expenses: ₹{summary['total_expenses']}",
        f"Total Savings: ₹{summary['total_savings']}",
        f"Savings Rate: {summary['savings_rate'] * 100:.1f}%",
        f"Average Daily Spending: ₹{summary['avg_daily_spending']}",
        f"Total Transactions: {summary['transaction_count']}",
        "",
        "Spending by Category:",
    ]
    for cat in categories:
        lines.append(f"  - {cat['category']}: ₹{cat['amount']} ({cat['percentage']}%)")

    lines.append("")
    lines.append("Monthly Breakdown:")
    for month in monthly:
        lines.append(
            f"  - {month['month']}: Income ₹{month['income']}, "
            f"Expenses ₹{month['expenses']}, Savings ₹{month['savings']}"
        )

    lines.append("")
    lines.append("Top Merchants:")
    for merchant in merchants:
        lines.append(
            f"  - {merchant['merchant']}: ₹{merchant['total_spent']} "
            f"({merchant['transaction_count']} transactions)"
        )

    return "\n".join(lines)


@router.post("")
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> dict:
    financial_context = build_financial_context(db)

    system_instruction = (
        "You are a personal finance assistant. You will be given the user's "
        "REAL financial data below, followed by their question.\n\n"
        f"{financial_context}\n\n"
        "RULES:\n"
        "1. Only use the numbers provided above. NEVER invent, estimate, or "
        "guess a number that isn't explicitly given.\n"
        "2. If the answer requires information not present above, say so "
        "clearly instead of guessing.\n"
        "3. Keep answers concise and in plain, friendly language.\n"
        "4. You may explain, compare, and summarize the given numbers, but "
        "never perform new calculations beyond simple arithmetic on the "
        "provided figures (e.g. you may state a difference between two "
        "given numbers, but do not fabricate any figure not derivable from "
        "the data above)."
    )

    response = generate_text(
        prompt=request.message,
        system_instruction=system_instruction,
    )

    return {"response": response}