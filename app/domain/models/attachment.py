"""
Attachment Model
"""

from typing import Optional
from sqlalchemy import BigInteger, String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Attachment(Base):
    """Attachment model - 거래 첨부파일 관리"""
    
    __tablename__ = "attachments"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mime: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    transaction: Mapped["Transaction"] = relationship(
        "Transaction",
        back_populates="attachments"
    )
    
    __table_args__ = (
        Index("attachments_transaction_id_fkey", "transaction_id"),
    )

