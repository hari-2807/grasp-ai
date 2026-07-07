from datetime import datetime

from api.services.sql_service import log_usage, get_monthly_upload_count, get_user

FREE_TIER_MONTHLY_LIMIT = 3

TRACKED_ACTIONS = {"upload", "summary", "analysis", "qa", "teaching", "flashcards"}


def record_action(user_id: str, action: str):
    """Log a usage event for a user. Silently ignores unrecognized action types."""
    if action not in TRACKED_ACTIONS:
        return
    log_usage(user_id, action=action)


def get_current_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def check_upload_allowed(user_id: str) -> dict:
    """Check whether a user can upload another document this month.

    Returns a dict with 'allowed' bool and remaining count info,
    rather than raising, so callers can decide how to respond.
    """
    user = get_user(user_id)
    if user is None:
        return {"allowed": False, "reason": "User not found"}

    if user["tier"] == "pro":
        return {"allowed": True, "tier": "pro", "uploads_remaining": None}

    month = get_current_month()
    count = get_monthly_upload_count(user_id, month_year=month)
    remaining = max(0, FREE_TIER_MONTHLY_LIMIT - count)

    return {
        "allowed": count < FREE_TIER_MONTHLY_LIMIT,
        "tier": "free",
        "uploads_this_month": count,
        "uploads_remaining": remaining,
        "reason": None if count < FREE_TIER_MONTHLY_LIMIT else (
            f"Free tier limit reached ({FREE_TIER_MONTHLY_LIMIT} uploads/month). "
            "Upgrade to Pro for unlimited uploads."
        ),
    }


def get_usage_summary(user_id: str) -> dict:
    """Return a usage summary for the current month, used for the /usage endpoint."""
    user = get_user(user_id)
    if user is None:
        return {"error": "User not found"}

    month = get_current_month()
    count = get_monthly_upload_count(user_id, month_year=month)

    return {
        "user_id": user_id,
        "month_year": month,
        "uploads_this_month": count,
        "tier": user["tier"],
        "uploads_remaining": None if user["tier"] == "pro" else max(0, FREE_TIER_MONTHLY_LIMIT - count),
    }
