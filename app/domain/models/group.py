"""
Group and GroupInvite Models
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.domain.models.user import User


class Group(Base):
    """Group model - 가족/커플 그룹 관리"""
    
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_groups"
    )
    members: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys="User.group_id",
        back_populates="group"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="group"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="group"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="group"
    )
    invites: Mapped[list["GroupInvite"]] = relationship(
        "GroupInvite",
        back_populates="group"
    )
    recurring_rules: Mapped[list["RecurringRule"]] = relationship(
        "RecurringRule",
        back_populates="group"
    )
    
    __table_args__ = (
        Index("groups_owner_id_fkey", "owner_id"),
    )


class GroupInvite(Base):
    """GroupInvite model - 그룹 초대 코드 관리"""
    
    __tablename__ = "group_invites"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False
    )
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    group: Mapped["Group"] = relationship(
        "Group",
        back_populates="invites"
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="group_invites"
    )
    
    __table_args__ = (
        Index("idx_group_invites_group", "group_id"),
        Index("idx_group_invites_expires", "expires_at"),
        Index("group_invites_created_by_fkey", "created_by"),
    )

