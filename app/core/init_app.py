import shutil

from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q
from tortoise import Tortoise

from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.log import logger
from app.models.admin import Api, Menu, Role
from app.models.house import Community, Ershoufang, DealRecord
from app.schemas.menus import MenuType
from app.settings.config import settings
from app.settings import TORTOISE_ORM

from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/docs",
                "/openapi.json",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


def register_routers(app: FastAPI, prefix: str = "/api"):
    app.include_router(api_router, prefix=prefix)


async def init_superuser():
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password="123456",
                is_active=True,
                is_superuser=True,
            )
        )


async def init_menus():
    menus = await Menu.exists()
    if not menus:
        # 1. 创建系统管理菜单
        system_menu = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="系统管理",
            path="/system",
            order=10,  # 保持与现有顺序一致
            parent_id=0,
            icon="carbon:gui-management",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/system/user",
        )

        # 系统管理子菜单
        system_children = [
            Menu(
                menu_type=MenuType.MENU,
                name="用户管理",
                path="user",
                order=1,
                parent_id=system_menu.id,
                icon="material-symbols:person-outline-rounded",
                is_hidden=False,
                component="/system/user",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="角色管理",
                path="role",
                order=2,
                parent_id=system_menu.id,
                icon="carbon:user-role",
                is_hidden=False,
                component="/system/role",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="菜单管理",
                path="menu",
                order=3,
                parent_id=system_menu.id,
                icon="material-symbols:list-alt-outline",
                is_hidden=False,
                component="/system/menu",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="API管理",
                path="api",
                order=4,
                parent_id=system_menu.id,
                icon="ant-design:api-outlined",
                is_hidden=False,
                component="/system/api",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="部门管理",
                path="dept",
                order=5,
                parent_id=system_menu.id,
                icon="mingcute:department-line",
                is_hidden=False,
                component="/system/dept",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="审计日志",
                path="auditlog",
                order=6,
                parent_id=system_menu.id,
                icon="ph:clipboard-text-bold",
                is_hidden=False,
                component="/system/auditlog",
                keepalive=False,
            ),
        ]
        await Menu.bulk_create(system_children)

        # 2. 创建房源管理菜单
        house_menu = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="房源管理",
            path="/house",
            order=3,
            parent_id=0,
            icon="material-symbols:home-work",
            is_hidden=False,
            component="/house",
            keepalive=False,
        )

        # 房源管理子菜单
        house_children = [
            Menu(
                menu_type=MenuType.MENU,
                name="小区信息",
                path="community",
                order=1,
                parent_id=house_menu.id,
                icon="material-symbols:home-work-outline",
                is_hidden=False,
                component="/house/community",
                keepalive=True,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="在售房源",
                path="ershoufang",
                order=2,
                parent_id=house_menu.id,
                icon="material-symbols:other-houses-outline-rounded",
                is_hidden=False,
                component="/house/ershoufang",
                keepalive=True,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="成交房源",
                path="deal-record",
                order=3,
                parent_id=house_menu.id,
                icon="material-symbols:in-home-mode-outline",
                is_hidden=False,
                component="/house/deal-record",
                keepalive=True,
            ),
        ]
        await Menu.bulk_create(house_children)

        # 3. 创建商机和项目管理菜单（作为顶级菜单）
        business_menus = [
            Menu(
                menu_type=MenuType.MENU,
                name="商机管理",
                path="/house/opportunity",
                order=1,
                parent_id=0,
                icon="mdi:floppy-variant",
                is_hidden=False,
                component="/house/opportunity",
                keepalive=True,
                redirect="/house/opportunity",
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="项目管理",
                path="/house/project",
                order=2,
                parent_id=0,
                icon="si:projects-alt-fill",
                is_hidden=False,
                component="/house/project",
                keepalive=True,
                redirect="/house/project",
            ),
        ]
        await Menu.bulk_create(business_menus)


async def init_apis():
    apis = await api_controller.model.exists()
    if not apis:
        await api_controller.refresh_api()


async def init_db():
    """初始化数据库"""
    try:
        # 初始化 Tortoise
        await Tortoise.init(config=TORTOISE_ORM)
        
        # 生成数据库表
        await Tortoise.generate_schemas()
        
        # 创建 deal_record 表
        await Tortoise.get_connection("default").execute_script("""
            CREATE TABLE IF NOT EXISTS "deal_record" (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                "community_id" INTEGER NOT NULL REFERENCES "community" ("id") ON DELETE CASCADE,
                "source" VARCHAR(20) NOT NULL,
                "source_transaction_id" VARCHAR(50),
                "deal_date" DATE NOT NULL,
                "total_price" FLOAT NOT NULL,
                "unit_price" FLOAT NOT NULL,
                "layout" VARCHAR(50),
                "size" FLOAT,
                "floor_info" VARCHAR(50),
                "orientation" VARCHAR(50),
                "building_year" INTEGER,
                "agency" VARCHAR(100),
                "deal_cycle" INTEGER,
                "house_link" VARCHAR(500),
                "layout_image" VARCHAR(500),
                "entry_time" TIMESTAMP,
                "original_data" JSON,
                "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await Tortoise.close_connections()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


async def init_roles():
    roles = await Role.exists()
    if not roles:
        admin_role = await Role.create(
            name="管理员",
            desc="管理员角色",
        )
        user_role = await Role.create(
            name="普通用户",
            desc="普通用户角色",
        )

        # 分配所有API给管理员角色
        all_apis = await Api.all()
        await admin_role.apis.add(*all_apis)
        # 分配所有菜单给管理员和普通用户
        all_menus = await Menu.all()
        await admin_role.menus.add(*all_menus)
        await user_role.menus.add(*all_menus)

        # 为普通用户分配基本API
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="基础模块"))
        await user_role.apis.add(*basic_apis)


async def init_data():
    await init_db()
    await init_superuser()
    await init_menus()
    await init_apis()
    await init_roles()


async def register_tortoise(app: FastAPI) -> None:
    """注册数据库连接"""
    await Tortoise.init(
        config=TORTOISE_ORM
    )
    logger.info("Tortoise-ORM started, %s, %s", Tortoise._connections, Tortoise.apps)
    await Tortoise.generate_schemas()
    
    # 注册关闭数据库连接
    app.add_event_handler("shutdown", lambda: Tortoise.close_connections())
