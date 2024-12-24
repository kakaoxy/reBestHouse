import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.settings import TORTOISE_ORM
from tortoise import Tortoise

async def fix_city_data():
    # 连接数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 获取数据库连接
    conn = Tortoise.get_connection("default")
    
    try:
        # 1. 删除现有数据
        await conn.execute_query("DELETE FROM community;")
        print("Deleted existing data")
        
        # 2. 插入新的测试数据
        await conn.execute_query("""
            INSERT INTO community 
            (name, city, region, area, address, building_type, property_rights, total_houses, building_year)
            VALUES 
            ('测试上海小区', 'shanghai', '浦东新区', '陆家嘴', '测试地址001号', '板楼', '商品房,动迁房', 2000, 2000),
            ('测试北京小区', 'beijing', '朝阳区', '望京', '测试地址002号', '板楼', '商品房', 1500, 2010);
        """)
        print("Inserted new test data")
        
        # 3. 验证数据
        result = await conn.execute_query("SELECT id, name, city FROM community;")
        print("Current data:", result)
        
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(fix_city_data()) 