"""
RecurringRule Model
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain.models.base import TimestampMixin
import enum


class RecurringFrequency(str, enum.Enum):
    """Recurring frequency enum"""
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"


class RecurringRule(Base, TimestampMixin):
    """RecurringRule model - 반복 거래 규칙 정의"""
    
    __tablename__ = "recurring_rules"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=True
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    frequency: Mapped[str] = mapped_column(
        SQLEnum(RecurringFrequency),
        nullable=False
    )
    day_rule: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("categories.id"),
        nullable=True
    )
    merchant: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    memo: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="recurring_rules"
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="recurring_rules"
    )
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="recurring_rules"
    )
    
    __table_args__ = (
        Index("idx_recurring_rules_group_active", "group_id", "is_active"),
        Index("idx_recurring_rules_creator_active", "created_by", "is_active"),
        Index("idx_recurring_rules_frequency_active", "frequency", "is_active"),
        Index("recurring_rules_category_id_fkey", "category_id"),
    )

