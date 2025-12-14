from fastapi import FastAPI

from api.middlewares import register_middlewares
from core.exceptions.errors_handlers import register_errors_handlers


def create_app() -> FastAPI:
    app = FastAPI()

    # Регистрация всех мидлварей
    register_middlewares(app)
    # Регистрация обработчиков ошибок
    register_errors_handlers(app)

    return app
