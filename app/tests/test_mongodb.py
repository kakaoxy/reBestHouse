import os
import sys
from pathlib import Path
from loguru import logger
from pprint import pprint
import traceback

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from app.core.mongo_config import mongodb

def test_mongodb_connection():
    """测试MongoDB连接并获取数据结构"""
    try:
        # 测试二手房在售数据
        logger.info("=== 测试二手房在售数据集合 ===")
        on_sale_doc = mongodb.collection_on_sale.find_one()
        if on_sale_doc:
            logger.info("在售房源集合访问成功")
            logger.info("数据字段结构:")
            pprint(list(on_sale_doc.keys()))
            logger.info("\n示例数据:")
            pprint(on_sale_doc)
        else:
            logger.warning("在售房源集合为空")

        # 测试成交房源数据
        logger.info("\n=== 测试成交房源数据集合 ===")
        sold_doc = mongodb.collection_sold.find_one()
        if sold_doc:
            logger.info("成交房源集合访问成功")
            logger.info("数据字段结构:")
            pprint(list(sold_doc.keys()))
            logger.info("\n示例数据:")
            pprint(sold_doc)
        else:
            logger.warning("成交房源集合为空")

        # 获取集合统计信息
        logger.info("\n=== 集合统计信息 ===")
        on_sale_count = mongodb.collection_on_sale.count_documents({})
        sold_count = mongodb.collection_sold.count_documents({})
        logger.info(f"在售房源数量: {on_sale_count}")
        logger.info(f"成交房源数量: {sold_count}")

        # 获取数据库中的所有集合
        logger.info("\n=== 数据库中的所有集合 ===")
        collections = mongodb.db.list_collection_names()
        logger.info(f"集合列表: {collections}")

    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
        raise

def test_query_examples():
    """测试一些常用查询示例"""
    try:
        logger.info("\n=== 查询示例 ===")
        
        # 示例1：按价格范围查询
        price_range_query = {
            "总价": {
                "$gte": 300,  
                "$lte": 500   
            }
        }
        price_range_count = mongodb.collection_on_sale.count_documents(price_range_query)
        logger.info(f"300-500万价格区间的房源数量: {price_range_count}")

        # 示例2：按户型查询（完全匹配）
        layout_query = {
            "户型": "2室1厅"
        }
        layout_count = mongodb.collection_on_sale.count_documents(layout_query)
        logger.info(f"2室1厅的房源数量: {layout_count}")

        # 示例3：按面积和总价组合查询
        combined_query = {
            "面积": {"$gte": 80, "$lte": 120},
            "总价": {"$lte": 600}
        }
        combined_count = mongodb.collection_on_sale.count_documents(combined_query)
        logger.info(f"80-120平米且总价不超过600万的房源数量: {combined_count}")

        # 示例4：按区域查询
        district_query = {
            "区域": "闵行"
        }
        district_count = mongodb.collection_on_sale.count_documents(district_query)
        logger.info(f"闵行区的房源数量: {district_count}")

        # 示例5：按建筑年代范围查询
        year_query = {
            "建筑年代": {
                "$gte": 2000,
                "$lte": 2010
            }
        }
        year_count = mongodb.collection_on_sale.count_documents(year_query)
        logger.info(f"2000-2010年建成的房源数量: {year_count}")

    except Exception as e:
        logger.error(f"查询示例测试过程中发生错误: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    logger.info("开始MongoDB连接测试...")
    test_mongodb_connection()
    test_query_examples()
    logger.info("MongoDB测试完成!") 