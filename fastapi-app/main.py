import asyncio

import uvicorn
from fastapi.staticfiles import StaticFiles

from api import router as api_router
from core import settings
from core.models import db_helper
from core.models.init_data import create_demo_data

from create_app import create_app

main_app = create_app()
# Подключение основного роутера
main_app.include_router(api_router)
# Подключение статики (автарки)
main_app.mount("/media", StaticFiles(directory="media"), name="media")


async def seed():
    print("Создаем демо данные...")
    async for session in db_helper.session_getter():
        await create_demo_data(session)


if __name__ == "__main__":
    asyncio.run(seed())
    uvicorn.run(
        "main:main_app",
        host=settings.httpserver_config.host,
        port=settings.httpserver_config.port,
        reload=True,
    )
