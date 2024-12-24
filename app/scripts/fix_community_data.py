from tortoise import Tortoise
from app.settings import TORTOISE_ORM
import asyncio

async def fix_community_data():
    # 连接数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 执行原始 SQL 来更新数据
    conn = Tortoise.get_connection("default")
    
    # 1. 先检查现有数据
    result = await conn.execute_query("""
        SELECT id, name, city FROM community;
    """)
    print("Current data:", result)
    
    # 2. 更新数据，确保城市值是小写的
    await conn.execute_query("""
        UPDATE community 
        SET city = LOWER(city)
        WHERE city IS NOT NULL;
    """)
    
    # 3. 再次检查数据
    result = await conn.execute_query("""
        SELECT id, name, city FROM community;
    """)
    print("After update:", result)
    
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(fix_community_data()) 