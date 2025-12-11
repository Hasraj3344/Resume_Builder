"""Usage tracking model for monthly limits."""

import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class UsageRecord(Base):
    """Usage record model for tracking monthly resume generations."""

    __tablename__ = "usage_records"

    __table_args__ = (
        UniqueConstraint("user_id", "month_year", name="unique_user_month"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    month_year = Column(String(7), nullable=False)  # Format: "2025-12"
    resumes_generated = Column(Integer, default=0, nullable=False)
    reset_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="usage_records")

    def __repr__(self):
        return f"<UsageRecord(id={self.id}, user_id={self.user_id}, month={self.month_year}, count={self.resumes_generated})>"

    @staticmethod
    def get_current_month_year() -> str:
        """Get current month-year string."""
        return datetime.now().strftime("%Y-%m")

    @staticmethod
    def get_next_reset_date() -> date:
        """Get the next reset date (1st of next month)."""
        now = datetime.now()
        if now.month == 12:
            return date(now.year + 1, 1, 1)
        return date(now.year, now.month + 1, 1)
