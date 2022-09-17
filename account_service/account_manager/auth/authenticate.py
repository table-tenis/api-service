from auth.jwt_handler import verify_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.database import redis_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/xface/v1/accounts/login")
from fastapi import Request
async def authenticate(request: Request, temp: str = Depends(oauth2_scheme)) -> str:
    authorization = request.headers.get('authorization')
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sign in for access"
        )
    if "Bearer" not in authorization:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Token Wrong Type"
        )
    token = authorization.split(" ")[1]
    decoded_token = verify_access_token(token)
    if redis_db.exists(token):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Token Blocked!"
        )
    return {"decoded_token" : decoded_token, "token" : token}