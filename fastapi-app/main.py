import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router as api_router
from api.middlewares import auth_middleware
from core import settings
from core.models import db_helper
from core.models.init_data import create_demo_data

app = FastAPI()
app.middleware("http")(auth_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
