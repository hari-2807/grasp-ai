import os
from fastapi import APIRouter, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from api.models.schemas import UserOut
from api.services.sql_service import get_user_by_email, create_user

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def _verify_google_token(credential: str) -> dict:
    """Verify a Google ID token server-side and return the decoded payload."""
    try:
        id_info = id_token.verify_oauth2_token(
            credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {e}")

    if id_info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=401, detail="Invalid token issuer")

    return id_info


@router.post("/google", response_model=UserOut)
def google_login(credential: str):
    """Verify a Google Sign-In credential and return or create the user."""
    id_info = _verify_google_token(credential)

    email = id_info.get("email")
    if not email or not id_info.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google account email not verified")

    user = get_user_by_email(email)
    if user is None:
        user = create_user(email=email, google_sub=id_info["sub"], tier="free")

    return user
