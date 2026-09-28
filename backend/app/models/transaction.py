from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Null for manually entered transactions
    upload_id: Mapped[int | None] = mapped_column(ForeignKey("uploads.id"), nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    description_raw: Mapped[str] = mapped_column(String(255))
    merchant: Mapped[str] = mapped_column(String(100), index=True)
    amount: Mapped[float] = mapped_column(Float)  # always positive
    type: Mapped[str] = mapped_column(String(10))  # "income" or "expense"
    category: Mapped[str] = mapped_column(String(50), index=True, default="Other")
    category_source: Mapped[str] = mapped_column(String(20), default="rule")  # rule / ml / llm / manual
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)

    upload = relationship("Upload", back_populates="transactions")