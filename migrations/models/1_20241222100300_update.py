from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "community" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(100) NOT NULL  /* 小区名称 */,
    "region" VARCHAR(50)   /* 区域 */,
    "area" VARCHAR(50)   /* 商圈 */,
    "address" VARCHAR(200)   /* 地址 */,
    "building_type" VARCHAR(50)   /* 建筑类型 */,
    "property_rights" VARCHAR(50)   /* 交易权属 */,
    "total_houses" INT   /* 房屋总数 */,
    "building_year" INT   /* 建筑年代 */,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP /* 创建时间 */,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP /* 更新时间 */
);
        CREATE TABLE IF NOT EXISTS "ershoufang" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "house_id" VARCHAR(50)   /* 房源ID */,
    "community_name" VARCHAR(100)   /* 小区名 */,
    "region" VARCHAR(50)   /* 区域 */,
    "area" VARCHAR(50)   /* 商圈 */,
    "layout" VARCHAR(50)   /* 户型描述 */,
    "size" REAL   /* 建筑面积 */,
    "floor" VARCHAR(50)   /* 楼层信息 */,
    "orientation" VARCHAR(50)   /* 房屋朝向 */,
    "ladder_ratio" VARCHAR(20)   /* 梯户比 */,
    "total_price" REAL NOT NULL  /* 房源总价 */,
    "unit_price" REAL   /* 房源单价 */,
    "listing_date" TIMESTAMP   /* 挂牌时间 */,
    "last_transaction_date" TIMESTAMP   /* 上次交易时间 */,
    "mortgage_info" VARCHAR(200)   /* 抵押信息 */,
    "layout_image" VARCHAR(500)   /* 户型图链接 */,
    "ke_code" VARCHAR(50)   /* 贝壳编号 */,
    "house_link" VARCHAR(500)   /* 房源链接 */,
    "city" VARCHAR(50)   /* 城市 */,
    "building_year" INT   /* 建筑年代 */,
    "building_structure" VARCHAR(50)   /* 楼栋结构 */,
    "data_source" VARCHAR(20) NOT NULL  /* 数据来源 */,
    "platform_listing_id" VARCHAR(50)   /* 来源平台房源ID */,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP /* 创建时间 */,
    "updated_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP /* 更新时间 */,
    "community_id" INT NOT NULL REFERENCES "community" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "community";
        DROP TABLE IF EXISTS "ershoufang";"""
