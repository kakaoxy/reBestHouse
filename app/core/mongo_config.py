import os
import traceback
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, AutoReconnect
from loguru import logger
from dotenv import load_dotenv
import time

# 加载.env文件
load_dotenv()

class MongoDBConfig:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # 重试延迟秒数
        
        for attempt in range(self.max_retries):
            try:
                # 获取环境变量，并提供默认值防止None
                MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
                MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
                MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
                MONGO_PORT = os.getenv("MONGO_PORT", "27017")
                MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")
                
                # 检查必要的环境变量是否存在
                if not all([MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT]):
                    raise ValueError("缺少必要的MongoDB环境变量配置")
                
                # 对用户名和密码进行URL编码
                encoded_username = quote_plus(MONGO_USERNAME)
                encoded_password = quote_plus(MONGO_PASSWORD)
                
                # 构建MongoDB连接URI
                MONGO_URI = f"mongodb://{encoded_username}:{encoded_password}@{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_SOURCE}"
                
                # 创建MongoDB客户端连接，添加连接配置
                self.client = MongoClient(
                    MONGO_URI,
                    connectTimeoutMS=5000,  # 连接超时时间
                    socketTimeoutMS=10000,  # socket超时时间
                    serverSelectionTimeoutMS=5000,  # 服务器选择超时时间
                    waitQueueTimeoutMS=5000,  # 连接池等待超时时间
                    retryWrites=True,  # 启用重试写入
                    maxPoolSize=50,  # 连接池最大连接数
                    minPoolSize=10,  # 连接池最小连接数
                    maxIdleTimeMS=50000,  # 连接最大空闲时间
                )
                
                # 验证连接
                self.client.server_info()
                logger.info("MongoDB连接验证成功")
                
                # 使用targethouse数据库
                self.db = self.client.targethouse
                
                # 输出所有集合名称
                collections = self.db.list_collection_names()
                logger.info(f"数据库中的所有集合: {collections}")
                
                # 获取或创建集合
                self.collection_on_sale = self.db.ershoufang
                self.collection_sold = self.db.chengjiao
                
                # 验证集合是否可访问
                test_query = self.collection_sold.find_one()
                if test_query:
                    logger.info("成交房源集合访问正常")
                    logger.debug(f"示例数据: {test_query}")
                else:
                    logger.warning("成交房源集合为空")
                
                # 如果成功连接，跳出重试循环
                break
                
            except (ConnectionFailure, AutoReconnect) as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"MongoDB连接失败，正在进行第{attempt + 1}次重试...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"MongoDB连接重试{self.max_retries}次后仍然失败")
                    raise
            except ValueError as ve:
                logger.error(f"配置错误: {ve}")
                raise
            except Exception as e:
                logger.error(f"数据库连接失败: {str(e)}")
                logger.error(traceback.format_exc())
                raise

    def __del__(self):
        """析构函数，确保关闭连接"""
        try:
            if hasattr(self, 'client'):
                self.client.close()
                logger.info("MongoDB连接已关闭")
        except Exception as e:
            logger.error(f"关闭MongoDB连接时发生错误: {str(e)}")

# 创建MongoDB配置实例
try:
    mongodb = MongoDBConfig()
except Exception as e:
    logger.error(f"MongoDB初始化失败: {str(e)}")
    # 在这里可以选择是否要继续抛出异常
    raise 