from datetime import date

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction


def _load_transactions_df(db: Session) -> pd.DataFrame:
    """Load all non-duplicate transactions into a DataFrame for analysis."""
    rows = db.execute(
        select(
            Transaction.date,
            Transaction.merchant,
            Transaction.amount,
            Transaction.type,
            Transaction.category,
        ).where(Transaction.is_duplicate == False)  # noqa: E712
    ).all()

    if not rows:
        return pd.DataFrame(columns=["date", "merchant", "amount", "type", "category"])

    df = pd.DataFrame(rows, columns=["date", "merchant", "amount", "type", "category"])
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_summary(db: Session) -> dict:
    df = _load_transactions_df(db)
    if df.empty:
        return {
            "total_income": 0.0, "total_expenses": 0.0, "total_savings": 0.0,
            "savings_rate": 0.0, "avg_daily_spending": 0.0, "transaction_count": 0,
        }

    income = float(df.loc[df["type"] == "income", "amount"].sum())
    expenses = float(df.loc[df["type"] == "expense", "amount"].sum())
    savings = income - expenses
    savings_rate = (savings / income) if income > 0 else 0.0

    expense_df = df.loc[df["type"] == "expense"]
    days_span = max((expense_df["date"].max() - expense_df["date"].min()).days + 1, 1) if not expense_df.empty else 1
    avg_daily_spending = expenses / days_span

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "total_savings": round(savings, 2),
        "savings_rate": round(savings_rate, 4),
        "avg_daily_spending": round(avg_daily_spending, 2),
        "transaction_count": int(len(df)),
    }


def get_category_breakdown(db: Session) -> list[dict]:
    df = _load_transactions_df(db)
    expenses = df.loc[df["type"] == "expense"]
    if expenses.empty:
        return []

    grouped = (
        expenses.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    total = grouped["amount"].sum()
    grouped["percentage"] = (grouped["amount"] / total * 100).round(1)
    grouped["amount"] = grouped["amount"].round(2)

    return grouped.to_dict(orient="records")


def get_monthly_breakdown(db: Session) -> list[dict]:
    df = _load_transactions_df(db)
    if df.empty:
        return []

    df["month"] = df["date"].dt.strftime("%Y-%m")
    grouped = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)

    for col in ("income", "expense"):
        if col not in grouped.columns:
            grouped[col] = 0.0

    grouped = grouped.reset_index().sort_values("month")
    grouped["savings"] = grouped["income"] - grouped["expense"]

    return [
        {
            "month": row["month"],
            "income": round(float(row["income"]), 2),
            "expenses": round(float(row["expense"]), 2),
            "savings": round(float(row["savings"]), 2),
        }
        for _, row in grouped.iterrows()
    ]


def get_daily_trend(db: Session) -> list[dict]:
    df = _load_transactions_df(db)
    expenses = df.loc[df["type"] == "expense"]
    if expenses.empty:
        return []

    grouped = expenses.groupby(expenses["date"].dt.strftime("%Y-%m-%d"))["amount"].sum().reset_index()
    grouped.columns = ["date", "amount"]
    grouped["amount"] = grouped["amount"].round(2)
    grouped = grouped.sort_values("date")

    return grouped.to_dict(orient="records")


def get_top_merchants(db: Session, limit: int = 10) -> list[dict]:
    df = _load_transactions_df(db)
    expenses = df.loc[df["type"] == "expense"]
    if expenses.empty:
        return []

    grouped = (
        expenses.groupby("merchant")["amount"]
        .agg(total_spent="sum", transaction_count="count")
        .sort_values("total_spent", ascending=False)
        .head(limit)
        .reset_index()
    )
    grouped["total_spent"] = grouped["total_spent"].round(2)

    return grouped.to_dict(orient="records")