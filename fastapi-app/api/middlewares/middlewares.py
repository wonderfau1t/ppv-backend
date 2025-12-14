from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from core.utils.jwt import decode_access_token

type CallNext = Callable[[Request], Awaitable[Response]]


def register_middlewares(app: FastAPI):
    # Корсы
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Аутентификация
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next: CallNext) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)
        # Паблик руты
        # TODO: избавиться от хардкода
        public_paths = {
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/docs",
            "/openapi.json",
        }

        if request.url.path in public_paths:
            return await call_next(request)

        token = request.cookies.get("access_token")
        if token is None:
            return JSONResponse({"error": "not authenticated"}, status_code=401)

        payload = decode_access_token(token)
        if payload is None:
            return JSONResponse({"error": "not valid token"}, status_code=401)

        # Запись claims в request.state.user
        request.state.user = payload

        return await call_next(request)
