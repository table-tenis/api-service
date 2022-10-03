import time
from datetime import datetime
from fastapi import HTTPException, status, Security
from jose import jwt, JWTError
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
# import sys, os
# dir = os.path.dirname(__file__)
# sys.path.insert(0, os.path.abspath(os.path.join(dir, '.')))
# sys.path.insert(0, os.path.abspath(os.path.join(dir, '..')))

from config.config import settings

def create_access_token(username: str):
    payload = {
        "username": username,
        "expires": time.time() + settings.TOKEN_EXPIRES
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def verify_access_token(token: str):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        expire = data.get("expires")

        if expire is None:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "No access token supplied"
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Token expired!"
            )
        return data

    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Invalid token"
        )
        
if __name__ == "__main__":
    token = create_access_token("tainp")