"""Subscription model for plan management."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class Subscription(Base):
    """Subscription model for managing user plans."""

    __tablename__ = "subscriptions"

    __table_args__ = (
        CheckConstraint(
            "plan_type IN ('free', 'pro')",
            name="check_plan_type"
        ),
        CheckConstraint(
            "status IN ('active', 'cancelled', 'expired')",
            name="check_status"
        ),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan_type = Column(String(50), nullable=False, default="free")
    status = Column(String(50), nullable=False, default="active")
    paypal_subscription_id = Column(String(255), unique=True, nullable=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    next_billing_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan={self.plan_type}, status={self.status})>"

    def is_pro(self) -> bool:
        """Check if subscription is pro plan."""
        return self.plan_type == "pro" and self.status == "active"
