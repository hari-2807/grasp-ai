import os
import stripe
from fastapi import APIRouter, HTTPException, Request

from api.models.schemas import CheckoutRequest, CheckoutResponse
from api.services.sql_service import get_user, update_user_tier, set_stripe_id

router = APIRouter(prefix="/payments", tags=["payments"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://grasp-ai.app")


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout_session(req: CheckoutRequest):
    """Create a Stripe Checkout session for the £5/month Pro upgrade."""
    user = get_user(req.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": STRIPE_PRO_PRICE_ID, "quantity": 1}],
            customer_email=user["email"],
            client_reference_id=req.user_id,
            success_url=f"{FRONTEND_URL}/upgrade/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{FRONTEND_URL}/upgrade/cancelled",
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return CheckoutResponse(checkout_url=session.url)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events — verifies signature before parsing anything."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("client_reference_id")
        stripe_customer_id = data.get("customer")
        if user_id:
            update_user_tier(user_id, "pro")
            set_stripe_id(user_id, stripe_customer_id)

    elif event_type in ("customer.subscription.deleted", "customer.subscription.paused"):
        stripe_customer_id = data.get("customer")
        _downgrade_by_customer_id(stripe_customer_id)

    elif event_type == "invoice.payment_failed":
        stripe_customer_id = data.get("customer")
        _downgrade_by_customer_id(stripe_customer_id)

    return {"status": "ok"}


def _downgrade_by_customer_id(stripe_customer_id: str):
    from api.services.sql_service import get_user_by_stripe_id
    user = get_user_by_stripe_id(stripe_customer_id)
    if user:
        update_user_tier(user["user_id"], "free")
