import os
import stripe

from api.services.sql_service import (
    update_user_tier,
    set_stripe_id,
    get_user_by_stripe_id,
)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


def verify_webhook_signature(payload: bytes, sig_header: str) -> dict:
    """Verify a Stripe webhook's signature and return the parsed event."""
    try:
        return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise ValueError(f"Invalid webhook signature: {e}")


def handle_event(event: dict) -> dict:
    """Route a verified Stripe event to the correct handler."""
    event_type = event["type"]
    data = event["data"]["object"]

    handlers = {
        "checkout.session.completed": _handle_checkout_completed,
        "customer.subscription.deleted": _handle_subscription_ended,
        "customer.subscription.paused": _handle_subscription_ended,
        "invoice.payment_failed": _handle_payment_failed,
    }

    handler = handlers.get(event_type)
    if handler is None:
        return {"status": "ignored", "type": event_type}

    handler(data)
    return {"status": "processed", "type": event_type}


def _handle_checkout_completed(data: dict):
    user_id = data.get("client_reference_id")
    stripe_customer_id = data.get("customer")
    if user_id:
        update_user_tier(user_id, "pro")
        set_stripe_id(user_id, stripe_customer_id)


def _handle_subscription_ended(data: dict):
    stripe_customer_id = data.get("customer")
    _downgrade_by_customer_id(stripe_customer_id)


def _handle_payment_failed(data: dict):
    stripe_customer_id = data.get("customer")
    _downgrade_by_customer_id(stripe_customer_id)


def _downgrade_by_customer_id(stripe_customer_id: str):
    user = get_user_by_stripe_id(stripe_customer_id)
    if user:
        update_user_tier(user["user_id"], "free")
