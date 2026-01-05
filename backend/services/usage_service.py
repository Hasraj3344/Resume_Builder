"""Usage tracking service for managing monthly resume generation limits."""

from datetime import datetime
from typing import Tuple, Dict
from sqlalchemy.orm import Session
from backend.models.usage import UsageRecord
from backend.models.subscription import Subscription


class UsageService:
    """Service for tracking and managing user usage limits."""

    # Plan limits
    FREE_TIER_LIMIT = 3
    PRO_TIER_LIMIT = None  # Unlimited

    @staticmethod
    def get_or_create_usage_record(db: Session, user_id: str) -> UsageRecord:
        """Get or create usage record for current month."""
        current_month = UsageRecord.get_current_month_year()

        # Try to get existing record
        usage = db.query(UsageRecord).filter(
            UsageRecord.user_id == user_id,
            UsageRecord.month_year == current_month
        ).first()

        # Create new record if doesn't exist
        if not usage:
            usage = UsageRecord(
                user_id=user_id,
                month_year=current_month,
                resumes_generated=0,
                reset_date=UsageRecord.get_next_reset_date()
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)

        return usage

    @staticmethod
    def check_can_generate(db: Session, user_id: str) -> Tuple[bool, str, Dict]:
        """
        Check if user can generate a resume.

        Returns:
            Tuple: (can_generate: bool, message: str, usage_info: Dict)
        """
        # Get user's subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()

        if not subscription:
            return False, "No active subscription found", {}

        # Pro users have unlimited access
        if subscription.is_pro():
            return True, "Unlimited access", {
                "plan": "pro",
                "limit": None,
                "used": 0,
                "remaining": None
            }

        # Free users have limits
        usage = UsageService.get_or_create_usage_record(db, user_id)

        if usage.resumes_generated >= UsageService.FREE_TIER_LIMIT:
            return False, f"Monthly limit of {UsageService.FREE_TIER_LIMIT} resumes reached. Upgrade to Pro for unlimited access.", {
                "plan": "free",
                "limit": UsageService.FREE_TIER_LIMIT,
                "used": usage.resumes_generated,
                "remaining": 0,
                "reset_date": usage.reset_date.isoformat()
            }

        remaining = UsageService.FREE_TIER_LIMIT - usage.resumes_generated
        return True, f"{remaining} resume(s) remaining this month", {
            "plan": "free",
            "limit": UsageService.FREE_TIER_LIMIT,
            "used": usage.resumes_generated,
            "remaining": remaining,
            "reset_date": usage.reset_date.isoformat()
        }

    @staticmethod
    def increment_usage(db: Session, user_id: str) -> UsageRecord:
        """Increment usage count for the user."""
        usage = UsageService.get_or_create_usage_record(db, user_id)
        usage.resumes_generated += 1
        db.commit()
        db.refresh(usage)
        return usage

    @staticmethod
    def get_usage_stats(db: Session, user_id: str) -> Dict:
        """Get usage statistics for the user."""
        # Get subscription info
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()

        if not subscription:
            return {
                "plan": None,
                "status": "no_subscription",
                "limit": 0,
                "used": 0,
                "remaining": 0
            }

        # Pro users
        if subscription.is_pro():
            usage = UsageService.get_or_create_usage_record(db, user_id)
            return {
                "plan": "pro",
                "status": "active",
                "limit": None,
                "used": usage.resumes_generated,
                "remaining": None,
                "reset_date": usage.reset_date.isoformat()
            }

        # Free users
        usage = UsageService.get_or_create_usage_record(db, user_id)
        remaining = max(0, UsageService.FREE_TIER_LIMIT - usage.resumes_generated)

        return {
            "plan": "free",
            "status": "active",
            "limit": UsageService.FREE_TIER_LIMIT,
            "used": usage.resumes_generated,
            "remaining": remaining,
            "reset_date": usage.reset_date.isoformat()
        }
