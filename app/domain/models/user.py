"""
User Model
"""

from typing import Optional
from sqlalchemy import BigInteger, String, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.domain.models.base import TimestampMixin


class User(Base, TimestampMixin):
    """User model - 사용자 기본 정보 및 계정 관리"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(60), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("groups.id"),
        nullable=True
    )
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True
    )
    
    # Relationships (with forward refs to avoid circular imports)
    group: Mapped[Optional["Group"]] = relationship(
        "Group",
        foreign_keys=[group_id],
        back_populates="members",
        remote_side="Group.id"
    )
    
    # One-to-many relationships
    owned_groups: Mapped[list["Group"]] = relationship(
        "Group",
        foreign_keys="[Group.owner_id]",
        back_populates="owner"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="owner",
        foreign_keys="[Transaction.owner_user_id]"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="creator",
        foreign_keys="[Category.created_by]"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="creator",
        foreign_keys="[Tag.created_by]"
    )
    group_invites: Mapped[list["GroupInvite"]] = relationship(
        "GroupInvite",
        back_populates="creator",
        foreign_keys="[GroupInvite.created_by]"
    )
    recurring_rules: Mapped[list["RecurringRule"]] = relationship(
        "RecurringRule",
        back_populates="creator",
        foreign_keys="[RecurringRule.created_by]"
    )
    
    __table_args__ = (
        Index("idx_users_group", "group_id"),
    )

