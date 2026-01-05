"""
PayPal Service - Integration with PayPal Subscriptions API
"""
import os
import requests
import base64
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class PayPalService:
    """Service for managing PayPal subscriptions"""

    def __init__(self):
        self.mode = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
        self.pro_plan_id = os.getenv("PAYPAL_PRO_PLAN_ID")

        # Set API base URL based on mode
        if self.mode == "sandbox":
            self.base_url = "https://api-m.sandbox.paypal.com"
        else:
            self.base_url = "https://api-m.paypal.com"

        self._access_token = None
        self._token_expiry = None

    def _get_access_token(self) -> str:
        """Get OAuth access token from PayPal"""
        # Check if we have a valid cached token
        if self._access_token and self._token_expiry:
            if datetime.now() < self._token_expiry:
                return self._access_token

        # Request new access token
        url = f"{self.base_url}/v1/oauth2/token"
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]

        # Cache token (expires in ~9 hours, we'll refresh after 8)
        from datetime import timedelta
        self._token_expiry = datetime.now() + timedelta(hours=8)

        return self._access_token

    def create_subscription(self, return_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Create a PayPal subscription for Pro plan

        Args:
            return_url: URL to redirect after successful subscription
            cancel_url: URL to redirect if user cancels

        Returns:
            {
                "subscription_id": str,
                "approval_url": str,
                "status": str
            }
        """
        if not self.pro_plan_id:
            raise ValueError("PayPal Pro Plan ID not configured")

        url = f"{self.base_url}/v1/billing/subscriptions"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "plan_id": self.pro_plan_id,
            "application_context": {
                "brand_name": "Resume Builder Pro",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "payment_method": {
                    "payer_selected": "PAYPAL",
                    "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
                },
                "return_url": return_url,
                "cancel_url": cancel_url
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()

        # Extract approval URL
        approval_url = None
        for link in data.get("links", []):
            if link.get("rel") == "approve":
                approval_url = link.get("href")
                break

        return {
            "subscription_id": data.get("id"),
            "approval_url": approval_url,
            "status": data.get("status")
        }

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details from PayPal

        Returns:
            {
                "id": str,
                "status": str,  # APPROVAL_PENDING, APPROVED, ACTIVE, SUSPENDED, CANCELLED, EXPIRED
                "plan_id": str,
                "start_time": str,
                "billing_info": {...}
            }
        """
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def cancel_subscription(self, subscription_id: str, reason: str = "User requested cancellation") -> bool:
        """
        Cancel a PayPal subscription

        Args:
            subscription_id: PayPal subscription ID
            reason: Cancellation reason

        Returns:
            True if successful
        """
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "reason": reason
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return True

    def suspend_subscription(self, subscription_id: str, reason: str = "Subscription suspended") -> bool:
        """Suspend a subscription (can be reactivated later)"""
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/suspend"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "reason": reason
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return True

    def activate_subscription(self, subscription_id: str, reason: str = "Subscription reactivated") -> bool:
        """Reactivate a suspended subscription"""
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/activate"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "reason": reason
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return True

    def verify_webhook_signature(self, headers: Dict, body: str) -> bool:
        """
        Verify PayPal webhook signature (for production)

        Args:
            headers: Request headers containing signature
            body: Raw request body

        Returns:
            True if signature is valid
        """
        url = f"{self.base_url}/v1/notifications/verify-webhook-signature"

        webhook_id = os.getenv("PAYPAL_WEBHOOK_ID")
        if not webhook_id:
            # In sandbox/development, skip verification
            return True

        auth_algo = headers.get("PAYPAL-AUTH-ALGO")
        cert_url = headers.get("PAYPAL-CERT-URL")
        transmission_id = headers.get("PAYPAL-TRANSMISSION-ID")
        transmission_sig = headers.get("PAYPAL-TRANSMISSION-SIG")
        transmission_time = headers.get("PAYPAL-TRANSMISSION-TIME")

        payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": webhook_id,
            "webhook_event": body
        }

        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result.get("verification_status") == "SUCCESS"

        return False
