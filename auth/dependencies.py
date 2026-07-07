from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

from auth.google_oauth import decode_token
from api.services.sql_service import get_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/google")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = decode_token(token, expected_type="access")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user(payload["sub"])
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
