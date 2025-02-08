from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise import Tortoise

from app.core.exceptions import SettingNotFound
from app.core.init_app import (
    init_data,
    make_middlewares,
    register_exceptions,
    register_routers,
)

try:
    from app.settings.config import settings
except ImportError:
    raise SettingNotFound("Can not import settings")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 确保静态文件目录存在
    os.makedirs("static/uploads/images", exist_ok=True)
    await init_data()
    yield
    await Tortoise.close_connections()


def create_app() -> FastAPI:
    print(f"Current working directory: {os.getcwd()}")
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )
    register_exceptions(app)
    register_routers(app, prefix="/api")
    
    # 确保静态文件目录存在
    os.makedirs("static/uploads/images", exist_ok=True)
    os.makedirs("static/project_materials", exist_ok=True)
    
    # 保持原有的静态文件挂载
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 添加 CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()
