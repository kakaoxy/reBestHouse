import asyncio
import os
import sys
from tabulate import tabulate

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.settings import TORTOISE_ORM
from tortoise import Tortoise

async def show_table_schemas():
    # 连接数据库
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    
    try:
        # 获取小区表结构
        community_schema = await conn.execute_query("""
            PRAGMA table_info(community);
        """)
        
        # 获取二手房表结构
        ershoufang_schema = await conn.execute_query("""
            PRAGMA table_info(ershoufang);
        """)
        
        # 格式化输出小区表结构
        print("\n=== Community Table Schema ===")
        community_headers = ["Column", "Type", "Nullable", "Default", "Description"]
        community_rows = []
        for col in community_schema[1]:
            community_rows.append([
                col[1],  # name
                col[2],  # type
                "YES" if not col[3] else "NO",  # nullable
                col[4] if col[4] is not None else "NULL",  # default
                get_community_column_description(col[1])  # description
            ])
        print(tabulate(community_rows, headers=community_headers, tablefmt="grid"))
        
        # 格式化输出二手房表结构
        print("\n=== Ershoufang Table Schema ===")
        ershoufang_headers = ["Column", "Type", "Nullable", "Default", "Description"]
        ershoufang_rows = []
        for col in ershoufang_schema[1]:
            ershoufang_rows.append([
                col[1],  # name
                col[2],  # type
                "YES" if not col[3] else "NO",  # nullable
                col[4] if col[4] is not None else "NULL",  # default
                get_ershoufang_column_description(col[1])  # description
            ])
        print(tabulate(ershoufang_rows, headers=ershoufang_headers, tablefmt="grid"))
        
    finally:
        await Tortoise.close_connections()

def get_community_column_description(column_name):
    descriptions = {
        "id": "Primary Key",
        "name": "小区名称",
        "city": "所在城市",
        "region": "所在区域",
        "area": "所在商圈",
        "address": "详细地址",
        "building_type": "建筑类型",
        "property_rights": "产权类型",
        "total_houses": "房屋总数",
        "building_year": "建筑年代",
        "created_at": "创建时间",
        "updated_at": "更新时间"
    }
    return descriptions.get(column_name, "")

def get_ershoufang_column_description(column_name):
    descriptions = {
        "id": "Primary Key",
        "community_id": "关联小区ID",
        "house_id": "房源编号",
        "community_name": "小区名称",
        "region": "所在区域",
        "area": "所在商圈",
        "layout": "户型",
        "size": "建筑面积",
        "floor": "楼层信息",
        "orientation": "房屋朝向",
        "ladder_ratio": "梯户比",
        "total_price": "总价(万)",
        "unit_price": "单价(元/平)",
        "listing_date": "挂牌时间",
        "last_transaction_date": "上次交易时间",
        "mortgage_info": "抵押信息",
        "layout_image": "户型图链接",
        "ke_code": "贝壳编号",
        "house_link": "房源链接",
        "city": "所在城市",
        "building_year": "建筑年代",
        "building_structure": "建筑结构",
        "data_source": "数据来源",
        "platform_listing_id": "平台房源ID",
        "created_at": "创建时间",
        "updated_at": "更新时间",
        "floor_number": "楼层",
        "total_floors": "总楼层"
    }
    return descriptions.get(column_name, "")

if __name__ == "__main__":
    asyncio.run(show_table_schemas()) 