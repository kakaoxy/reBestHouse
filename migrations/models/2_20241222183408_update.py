from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "ershoufang" ADD "floor_number" INT   /* 楼层 */;
        ALTER TABLE "ershoufang" ADD "total_floors" INT   /* 总楼层 */;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "ershoufang" DROP COLUMN "floor_number";
        ALTER TABLE "ershoufang" DROP COLUMN "total_floors";"""
