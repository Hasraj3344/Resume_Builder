"""Password Reset Token Model"""
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timedelta
from ..database import Base


class PasswordResetToken(Base):
    """Password reset token model"""
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_valid(self):
        """Check if token is valid (not expired and not used)"""
        return not self.used and datetime.utcnow() < self.expires_at

    @staticmethod
    def create_expiry():
        """Create expiry time (1 hour from now)"""
        return datetime.utcnow() + timedelta(hours=1)
