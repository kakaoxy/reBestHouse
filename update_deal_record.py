import sqlite3

def create_deal_record_table():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # 1. 删除已存在的表和索引
        cursor.execute("DROP TABLE IF EXISTS deal_record")
        cursor.execute("DROP INDEX IF EXISTS idx_deal_record_created_at")
        cursor.execute("DROP INDEX IF EXISTS idx_deal_record_updated_at")
        print("已删除旧的表和索引")
        
        # 2. 创建新表 (添加字段说明)
        cursor.execute("""
        CREATE TABLE deal_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,                 -- 主键ID
            house_id VARCHAR(50),                                          -- 房源ID
            community_id INTEGER NOT NULL REFERENCES community(id),        -- 小区ID
            community_name VARCHAR(100) NOT NULL,                         -- 小区名称
            region VARCHAR(50) NOT NULL,                                  -- 所在区域
            area VARCHAR(50) NOT NULL,                                    -- 所在商圈
            layout VARCHAR(50),                                           -- 户型
            size REAL NOT NULL,                                          -- 建筑面积
            floor_info VARCHAR(50),                                       -- 楼层信息
            floor_number INTEGER,                                         -- 所在楼层
            total_floors INTEGER,                                         -- 总楼层
            orientation VARCHAR(50),                                      -- 房屋朝向
            listing_price REAL,                                          -- 挂牌价
            total_price REAL NOT NULL,                                   -- 成交价
            unit_price REAL,                                             -- 单价(元/平)
            deal_date DATE NOT NULL,                                     -- 成交时间
            deal_cycle INTEGER,                                          -- 成交周期
            tags VARCHAR(200),                                           -- 标签
            layout_image VARCHAR(500),                                   -- 户型图链接
            house_link VARCHAR(500),                                     -- 房源链接
            city VARCHAR(50) NOT NULL,                                   -- 所在城市
            building_year INTEGER,                                       -- 建筑年代
            building_structure VARCHAR(50),                              -- 建筑结构
            location VARCHAR(200),                                       -- 位置
            decoration VARCHAR(50),                                      -- 装修
            agency VARCHAR(100),                                         -- 中介公司
            source VARCHAR(50) NOT NULL,                                 -- 数据来源
            source_transaction_id VARCHAR(50),                           -- 来源平台交易ID
            entry_time TIMESTAMP,                                        -- 数据入库时间
            original_data JSON,                                          -- 原始数据
            data_source VARCHAR(50),                                     -- 数据来源(已废弃)
            platform_listing_id VARCHAR(50),                             -- 平台房源ID(已废弃)
            created_at TIMESTAMP NOT NULL,                               -- 创建时间
            updated_at TIMESTAMP NOT NULL                                -- 更新时间
        )
        """)
        print("已创建新表")
        
        # 3. 创建索引
        cursor.execute("CREATE INDEX idx_deal_record_created_at ON deal_record(created_at)")
        cursor.execute("CREATE INDEX idx_deal_record_updated_at ON deal_record(updated_at)")
        print("已创建索引")
        
        # 4. 提交更改
        conn.commit()
        
        # 5. 显示表结构
        print("\n表结构:")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='deal_record'")
        table_sql = cursor.fetchone()[0]
        print(table_sql)
        
        print("\n表结构创建完成!")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        conn.rollback()
        print("已回滚所有更改")
        raise
    finally:
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    create_deal_record_table()