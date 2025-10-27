"""
Category Model
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
# TransactionType enum is in transaction.py


class Category(Base):
    """Category model - 거래 분류 카테고리 관리"""
    
    __tablename__ = "categories"
    
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
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # TransactionType enum
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    budget_amount: Mapped[Optional[int]] = mapped_column(BigInteger, default=0, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="categories"
    )
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="categories"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="category"
    )
    recurring_rules: Mapped[list["RecurringRule"]] = relationship(
        "RecurringRule",
        back_populates="category"
    )
    
    __table_args__ = (
        UniqueConstraint("group_id", "name", "type", name="ux_category_name"),
        Index("idx_categories_group", "group_id"),
        Index("idx_categories_creator", "created_by"),
    )

