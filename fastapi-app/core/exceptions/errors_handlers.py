from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .auth import *
from .crud import *


def register_errors_handlers(app: FastAPI) -> None:
    # Ошибки валидации
    @app.exception_handler(ValidationError)
    def handle_pydantic_errors(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"message": "Validation error", "errors": exc.errors()},
        )

    # Внутренние ошибки приложения
    @app.exception_handler(AppError)
    def handle_app_error(request: Request, exc: AppError):
        match exc:
            case UnauthorizedError():
                _status = status.HTTP_401_UNAUTHORIZED
                detail = "Not authenticated"

            case InvalidCredentialsError():
                _status = status.HTTP_401_UNAUTHORIZED
                detail = "Invalid credentials"

            case ForbiddenError():
                _status = status.HTTP_403_FORBIDDEN
                detail = "Insufficient rights"

            case NotFoundError():
                _status = status.HTTP_404_NOT_FOUND
                detail = str(exc)

            case AlreadyExistsError():
                _status = status.HTTP_409_CONFLICT
                detail = str(exc)

            case _:
                _status = status.HTTP_500_INTERNAL_SERVER_ERROR
                detail = "Internal server error"

        return JSONResponse(status_code=_status, content={"message": detail})
