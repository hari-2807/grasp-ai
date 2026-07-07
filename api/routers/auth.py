from fastapi import APIRouter, HTTPException

from api.models.schemas import UserOut
from api.services.sql_service import get_user_by_email, create_user
from auth.google_oauth import verify_google_credential, create_token_pair, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google")
def google_login(credential: str):
    try:
        id_info = verify_google_credential(credential)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    email = id_info["email"]
    user = get_user_by_email(email)
    if user is None:
        user = create_user(email=email, google_sub=id_info["sub"], tier="free")

    tokens = create_token_pair(user["user_id"])
    return {**tokens, "user": UserOut(**user)}


@router.post("/refresh")
def refresh(refresh_token: str):
    try:
        new_access_token = refresh_access_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return {"access_token": new_access_token, "token_type": "bearer"}

