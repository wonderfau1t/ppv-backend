from typing import Annotated

from fastapi import Depends, HTTPException, Request

from core.schemas.auth import JWTClaims
from core.utils.jwt import decode_access_token


# def auth_required(request: Request) -> JWTClaims:
#     token = request.cookies.get("access_token")

#     if token is None:
#         raise HTTPException(status_code=401, detail={"error": "not authenticated"})

#     try:
#         payload = decode_access_token(token)
#         return payload
#     except Exception:
#         raise HTTPException(status_code=401, detail={"error": "not valid token"})


# def role_required(required_role: list[str]):
#     def wrapper(user: Annotated[JWTClaims, Depends(auth_required)]):
#         if user.role not in required_role:
#             raise HTTPException(
#                 status_code=403, detail="Access forbidden: insufficient permissions"
#             )
#         return user

#     return wrapper
