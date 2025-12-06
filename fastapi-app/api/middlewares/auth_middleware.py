from typing import Awaitable, Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.utils.jwt import decode_access_token

type CallNext = Callable[[Request], Awaitable[Response]]


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        # Паблик руты
        # TODO: избавиться от хардкода
        public_paths = {
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/docs",
            "/openapi.json",
        }

        print(request.url.path)
        if request.url.path in public_paths:
            return await call_next(request)

        token = request.cookies.get("access_token")
        if token is None:
            raise HTTPException(status_code=401, detail={"error": "not authenticated"})
        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail={"error": "not valid token"})

        # Запись claims в request.state.user
        request.state.user = payload

        return await call_next(request)
