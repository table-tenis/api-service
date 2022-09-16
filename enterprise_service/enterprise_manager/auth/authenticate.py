from auth.jwt_handler import verify_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.database import redis_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/xface/v1/acc/accounts/login")

async def authenticate(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )

    decoded_token = verify_access_token(token)
    if redis_db.exists(token):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Token Blocked!"
        )
    return {"decoded_token" : decoded_token, "token" : token}