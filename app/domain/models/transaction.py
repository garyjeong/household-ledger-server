"""
Transaction Model
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Date, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain.models.base import TimestampMixin
import enum


class TransactionType(str, enum.Enum):
    """Transaction type enum"""
    EXPENSE = "EXPENSE"
    INCOME = "INCOME"
    TRANSFER = "TRANSFER"


class Transaction(Base, TimestampMixin):
    """Transaction model - 거래 내역 중심 테이블"""
    
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("groups.id"),
        nullable=True
    )
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    type: Mapped[str] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False
    )
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("categories.id"),
        nullable=True
    )
    tag_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("tags.id"),
        nullable=True
    )
    merchant: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    memo: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="transactions"
    )
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="transactions"
    )
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="transactions"
    )
    tag: Mapped[Optional["Tag"]] = relationship(
        "Tag",
        back_populates="transactions"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="transaction"
    )
    
    __table_args__ = (
        Index("idx_tx_group_date", "group_id", "date"),
        Index("idx_tx_owner_date", "owner_user_id", "date"),
        Index("idx_tx_category", "category_id"),
        Index("idx_tx_tag", "tag_id"),
    )

