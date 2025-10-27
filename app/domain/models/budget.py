"""
Budget Model
"""

from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.domain.models.base import TimestampMixin
import enum


class OwnerType(str, enum.Enum):
    """Owner type enum"""
    USER = "USER"
    GROUP = "GROUP"


class BudgetStatus(str, enum.Enum):
    """Budget status enum"""
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DRAFT = "DRAFT"


class Budget(Base, TimestampMixin):
    """Budget model - 월별 예산 관리"""
    
    __tablename__ = "budgets"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_type: Mapped[str] = mapped_column(
        SQLEnum(OwnerType),
        nullable=False
    )
    owner_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    total_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(BudgetStatus),
        default=BudgetStatus.ACTIVE,
        nullable=False
    )
    
    __table_args__ = (
        UniqueConstraint("owner_type", "owner_id", "period", name="ux_budget_owner_period"),
        Index("idx_budgets_owner", "owner_type", "owner_id"),
    )

