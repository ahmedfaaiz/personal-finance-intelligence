from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    rows_total: Mapped[int] = mapped_column(Integer, default=0)
    rows_accepted: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)

    transactions = relationship("Transaction", back_populates="upload", cascade="all, delete-orphan")
    rejected_rows = relationship("RejectedRow", back_populates="upload", cascade="all, delete-orphan")
    cleaning_logs = relationship("CleaningLog", back_populates="upload", cascade="all, delete-orphan")


class RejectedRow(Base):
    __tablename__ = "rejected_rows"

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"))
    row_number: Mapped[int] = mapped_column(Integer)
    raw_data: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(String(255))

    upload = relationship("Upload", back_populates="rejected_rows")


class CleaningLog(Base):
    __tablename__ = "cleaning_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[int] = mapped_column(ForeignKey("uploads.id"))
    row_number: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(100))
    before_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    after_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    upload = relationship("Upload", back_populates="cleaning_logs")