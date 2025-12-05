from datetime import datetime, timedelta

import jwt

from core.config import settings
from core.schemas.auth import JWTClaims


def create_access_token(claims: JWTClaims) -> str:
    to_encode = claims.model_dump()
    expire = datetime.now() + timedelta(minutes=settings.jwt.ttl_minutes)
    to_encode["exp"] = expire

    token = jwt.encode(
        payload=to_encode,
        key=settings.jwt.secret,
        algorithm=settings.jwt.algorithm,
    )
    return token


def decode_access_token(token: str) -> JWTClaims:
    try:
        payload = jwt.decode(
            jwt=token, key=settings.jwt.secret, algorithms=[settings.jwt.algorithm]
        )
        return JWTClaims(**payload)
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
