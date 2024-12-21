import os
import traceback
from urllib.parse import quote_plus
from pymongo import MongoClient
from loguru import logger

class MongoDBConfig:
    def __init__(self):
        try:
            MONGO_USERNAME = quote_plus(os.getenv("MONGO_USERNAME"))
            MONGO_PASSWORD = quote_plus(os.getenv("MONGO_PASSWORD"))
            MONGO_HOST = os.getenv("MONGO_HOST")
            MONGO_PORT = os.getenv("MONGO_PORT")
            MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE")
            
            MONGO_URI = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_SOURCE}"
            
            self.client = MongoClient(MONGO_URI)
            # 验证连接
            self.client.server_info()
            
            # 使用targethouse数据库
            self.db = self.client.targethouse
            
            # 输出所有集合名称
            collections = self.db.list_collection_names()
            logger.info(f"数据库中的所有集合: {collections}")
            
            # 获取或创建集合
            self.collection_on_sale = self.db.ershoufang
            self.collection_sold = self.db.chengjiao
            
            logger.info("数据库连接成功")
            
            # 验证集合是否可访问
            test_query = self.collection_sold.find_one()
            if test_query:
                logger.info("成交房源集合访问正常")
                logger.info(f"示例数据: {test_query}")
            else:
                logger.warning("成交房源集合为空")
                
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            logger.error(traceback.format_exc())
            raise

mongodb = MongoDBConfig() 