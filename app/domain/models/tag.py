"""
Tag Model
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Tag(Base):
    """Tag model - 거래 태그 시스템"""
    
    __tablename__ = "tags"
    
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
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="tags"
    )
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        back_populates="tags"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="tag"
    )
    
    __table_args__ = (
        UniqueConstraint("group_id", "name", name="ux_tag"),
        Index("idx_tags_group", "group_id"),
        Index("tags_created_by_fkey", "created_by"),
    )

