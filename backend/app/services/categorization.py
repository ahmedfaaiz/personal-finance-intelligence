import re
from dataclasses import dataclass

CATEGORIES = [
    "Food", "Groceries", "Transportation", "Shopping", "Entertainment",
    "Bills", "Healthcare", "Education", "Travel", "Subscriptions",
    "Rent", "Salary", "Investment", "Other",
]

# Level 1: keyword -> category. Checked against the normalized merchant name
# (lowercased). Order doesn't matter; first match wins.
RULES: list[tuple[str, str]] = [
    # Food & delivery
    (r"swiggy|zomato|restaurant|cafe|dominos|mcdonald|kfc|starbucks", "Food"),
    # Groceries
    (r"dmart|big\s?basket|grofers|blinkit|zepto|grocery|supermarket", "Groceries"),
    # Transportation
    (r"\buber\b|\bola\b|rapido|metro|petrol|fuel|parking|taxi", "Transportation"),
    # Shopping
    (r"amazon|flipkart|myntra|ajio|meesho|mall|shopping", "Shopping"),
    # Entertainment
    (r"bookmyshow|pvr|inox|cinema|movie|game", "Entertainment"),
    # Subscriptions
    (r"netflix|spotify|prime\s?video|hotstar|youtube\s?premium|subscription", "Subscriptions"),
    # Bills / utilities
    (r"electricity|water\s?bill|broadband|wifi|mobile\s?recharge|dth|gas\s?bill", "Bills"),
    # Healthcare
    (r"pharmacy|hospital|clinic|doctor|medical|apollo|medlife|pharmeasy", "Healthcare"),
    # Education
    (r"udemy|coursera|tuition|school|college|university|course", "Education"),
    # Travel
    (r"makemytrip|goibibo|airbnb|indigo|airline|flight|hotel|irctc", "Travel"),
    # Rent
    (r"\brent\b|landlord", "Rent"),
    # Salary / income
    (r"salary|payroll|stipend", "Salary"),
    # Investment
    (r"mutual\s?fund|zerodha|groww|upstox|sip\b|investment", "Investment"),
]


@dataclass
class CategorizationResult:
    category: str
    source: str  # "rule" | "ml" | "default"
    confidence: float | None = None


def categorize_rule_based(merchant: str, description: str) -> CategorizationResult | None:
    """Try Level 1 keyword matching. Returns None if nothing matches."""
    text = f"{merchant} {description}".lower()
    for pattern, category in RULES:
        if re.search(pattern, text):
            return CategorizationResult(category=category, source="rule")
    return None