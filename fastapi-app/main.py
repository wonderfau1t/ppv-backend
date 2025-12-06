import asyncio

import uvicorn
from fastapi import FastAPI

from api import router as api_router
from api.middlewares import AuthMiddleware
from core import settings
from core.models import db_helper
from core.models.init_data import create_demo_data

app = FastAPI()
app.add_middleware(AuthMiddleware)
app.include_router(api_router)


async def seed():
    print("Создаем демо данные...")
    async for session in db_helper.session_getter():
        await create_demo_data(session)


if __name__ == "__main__":
    asyncio.run(seed())
    uvicorn.run(
        "main:app",
        host=settings.httpserver_config.host,
        port=settings.httpserver_config.port,
        reload=True,
    )
