"""
Subscription API Router - Endpoints for subscription management
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..models.subscription import Subscription
from ..services.paypal_service import PayPalService
from ..services.usage_service import UsageService

router = APIRouter()
paypal_service = PayPalService()


class CreateSubscriptionRequest(BaseModel):
    return_url: str = "http://localhost:3000/subscription/success"
    cancel_url: str = "http://localhost:3000/subscription/cancel"


class ActivateSubscriptionRequest(BaseModel):
    subscription_id: str


@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current subscription status"""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()

    if not subscription:
        return {
            "plan": "free",
            "status": "active",
            "subscription_id": None,
            "next_billing_date": None
        }

    return {
        "plan": subscription.plan_type,
        "status": subscription.status,
        "subscription_id": subscription.paypal_subscription_id,
        "next_billing_date": subscription.next_billing_date.isoformat() if subscription.next_billing_date else None,
        "start_date": subscription.start_date.isoformat() if subscription.start_date else None
    }


@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get usage statistics"""
    stats = UsageService.get_usage_stats(db, str(current_user.id))
    return stats


@router.post("/create-pro")
async def create_pro_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a PayPal Pro subscription

    Returns approval URL to redirect user to PayPal
    """
    try:
        # Check if user already has an active Pro subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.plan_type == "pro",
            Subscription.status == "active"
        ).first()

        if existing_sub:
            raise HTTPException(
                status_code=400,
                detail="User already has an active Pro subscription"
            )

        # Create subscription in PayPal
        paypal_response = paypal_service.create_subscription(
            return_url=request.return_url,
            cancel_url=request.cancel_url
        )

        subscription_id = paypal_response["subscription_id"]
        approval_url = paypal_response["approval_url"]

        # Create pending subscription record in database
        # Will be activated via webhook when user completes payment
        subscription = Subscription(
            user_id=current_user.id,
            plan_type="pro",
            status="pending",
            paypal_subscription_id=subscription_id,
            start_date=None,
            next_billing_date=None
        )
        db.add(subscription)
        db.commit()

        return {
            "subscription_id": subscription_id,
            "approval_url": approval_url,
            "message": "Redirect user to approval_url to complete subscription"
        }

    except Exception as e:
        print(f"[SUBSCRIPTION] Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.post("/activate")
async def activate_subscription(
    request: ActivateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Activate subscription after PayPal approval
    Called from frontend after user returns from PayPal
    """
    try:
        subscription_id = request.subscription_id

        # Get subscription from database
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.paypal_subscription_id == subscription_id
        ).first()

        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="Subscription not found"
            )

        # Get subscription details from PayPal
        paypal_sub = paypal_service.get_subscription(subscription_id)

        # Update subscription status
        subscription.status = paypal_sub["status"].lower()
        subscription.start_date = datetime.now()

        # Calculate next billing date (30 days from now)
        subscription.next_billing_date = datetime.now() + timedelta(days=30)

        # Deactivate old free subscription
        old_subs = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.id != subscription.id,
            Subscription.status == "active"
        ).all()

        for old_sub in old_subs:
            old_sub.status = "cancelled"

        db.commit()
        db.refresh(subscription)

        return {
            "message": "Subscription activated successfully",
            "plan": subscription.plan_type,
            "status": subscription.status,
            "next_billing_date": subscription.next_billing_date.isoformat()
        }

    except Exception as e:
        print(f"[SUBSCRIPTION] Error activating subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate subscription: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Cancel active Pro subscription"""
    try:
        # Get active Pro subscription
        subscription = db.query(Subscription).filter(
            Subscription.user_id == current_user.id,
            Subscription.plan_type == "pro",
            Subscription.status == "active"
        ).first()

        if not subscription:
            raise HTTPException(
                status_code=404,
                detail="No active Pro subscription found"
            )

        # Cancel in PayPal
        paypal_service.cancel_subscription(
            subscription.paypal_subscription_id,
            reason="User requested cancellation"
        )

        # Update database
        subscription.status = "cancelled"
        db.commit()

        # Create new free subscription
        free_sub = Subscription(
            user_id=current_user.id,
            plan_type="free",
            status="active",
            paypal_subscription_id=None,
            start_date=datetime.now(),
            next_billing_date=None
        )
        db.add(free_sub)
        db.commit()

        return {
            "message": "Subscription cancelled successfully. You've been moved to the Free plan.",
            "plan": "free",
            "status": "active"
        }

    except Exception as e:
        print(f"[SUBSCRIPTION] Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/webhook")
async def paypal_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle PayPal webhook events

    Events we care about:
    - BILLING.SUBSCRIPTION.ACTIVATED
    - BILLING.SUBSCRIPTION.CANCELLED
    - BILLING.SUBSCRIPTION.EXPIRED
    - BILLING.SUBSCRIPTION.SUSPENDED
    - PAYMENT.SALE.COMPLETED
    """
    try:
        # Get raw body and headers
        body = await request.body()
        headers = dict(request.headers)

        # Verify webhook signature (in production)
        # if not paypal_service.verify_webhook_signature(headers, body.decode()):
        #     raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Parse event data
        import json
        event = json.loads(body)

        event_type = event.get("event_type")
        resource = event.get("resource", {})
        subscription_id = resource.get("id")

        print(f"[WEBHOOK] Received event: {event_type} for subscription: {subscription_id}")

        # Find subscription in database
        subscription = db.query(Subscription).filter(
            Subscription.paypal_subscription_id == subscription_id
        ).first()

        if not subscription:
            print(f"[WEBHOOK] Subscription not found: {subscription_id}")
            return {"status": "ignored", "reason": "subscription not found"}

        # Handle different event types
        if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
            subscription.status = "active"
            subscription.start_date = datetime.now()
            subscription.next_billing_date = datetime.now() + timedelta(days=30)

        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            subscription.status = "cancelled"

        elif event_type == "BILLING.SUBSCRIPTION.EXPIRED":
            subscription.status = "expired"

        elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
            subscription.status = "suspended"

        elif event_type == "PAYMENT.SALE.COMPLETED":
            # Payment received, update next billing date
            subscription.next_billing_date = datetime.now() + timedelta(days=30)

        db.commit()

        print(f"[WEBHOOK] Subscription {subscription_id} updated to status: {subscription.status}")

        return {
            "status": "success",
            "event_type": event_type,
            "subscription_id": subscription_id
        }

    except Exception as e:
        print(f"[WEBHOOK] Error processing webhook: {str(e)}")
        import traceback
        print(traceback.format_exc())
        # Return 200 to acknowledge receipt even if processing failed
        return {"status": "error", "message": str(e)}
