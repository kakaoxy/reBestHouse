from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.house import Community, Ershoufang, DealRecord

# Community Schemas
class CommunityBase(BaseModel):
    name: str
    city: str
    region: str
    area: str
    address: Optional[str] = None
    building_type: Optional[str] = None
    property_rights: Optional[str] = None
    total_houses: Optional[int] = None
    building_year: Optional[int] = None

class CommunityCreate(CommunityBase):
    pass

class CommunityUpdate(CommunityBase):
    id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    address: Optional[str] = None
    building_type: Optional[str] = None
    property_rights: Optional[str] = None
    total_houses: Optional[int] = None
    building_year: Optional[int] = None

class CommunityInDB(CommunityBase):
    id: int

    class Config:
        from_attributes = True

class CommunityList(BaseModel):
    items: List[CommunityInDB]
    total: int
    page: int
    page_size: int

# 保留原有的响应模型
CommunityResponse = pydantic_model_creator(
    Community,
    name="CommunityResponse",
    exclude=("houses",)  # 排除反向关系字段
)

# Ershoufang Schemas
class ErshoufangBase(BaseModel):
    community_id: int = Field(..., description='小区ID')
    house_id: Optional[str] = Field(None, description='房源ID')
    community_name: Optional[str] = Field(None, description='小区名')
    region: Optional[str] = Field(None, description='区域')
    area: Optional[str] = Field(None, description='商圈')
    layout: Optional[str] = Field(None, description='户型描述')
    size: Optional[float] = Field(None, description='建筑面积')
    floor: Optional[str] = Field(None, description='楼层信息')
    orientation: Optional[str] = Field(None, description='房屋朝向')
    ladder_ratio: Optional[str] = Field(None, description='梯户比')
    total_price: float = Field(..., description='房源总价')
    unit_price: Optional[float] = Field(None, description='房源单价')
    listing_date: Optional[datetime] = Field(None, description='挂牌时间')
    last_transaction_date: Optional[datetime] = Field(None, description='上次交易时间')
    mortgage_info: Optional[str] = Field(None, description='抵押信息')
    layout_image: Optional[str] = Field(None, description='户型图链接')
    ke_code: Optional[str] = Field(None, description='贝壳编号')
    house_link: Optional[str] = Field(None, description='房源链接')
    city: Optional[str] = Field(None, description='城市')
    building_year: Optional[int] = Field(None, description='建筑年代')
    building_structure: Optional[str] = Field(None, description='楼栋结构')
    data_source: str = Field(..., description='数据来源')
    platform_listing_id: Optional[str] = Field(None, description='来源平台房源ID')

class ErshoufangCreate(BaseModel):
    community_id: Optional[int] = None
    community_name: str
    region: Optional[str] = None
    area: Optional[str] = None
    layout: str
    floor_number: int
    total_floors: int
    orientation: Optional[str] = None
    size: float
    total_price: float
    data_source: str
    city: str = 'shanghai'

class ErshoufangUpdate(ErshoufangBase):
    community_id: Optional[int] = Field(None, description='小区ID')
    total_price: Optional[float] = Field(None, description='房源总价')
    data_source: Optional[str] = Field(None, description='数据来源')
    city: Optional[str] = Field('shanghai', description='城市')

class ErshoufangInDB(ErshoufangBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response Models
ErshoufangResponse = pydantic_model_creator(
    Ershoufang,
    name="ErshoufangResponse",
    include=(
        "id", "community_id", "house_id", "community_name", "region",
        "area", "layout", "size", "floor", "orientation", "ladder_ratio",
        "total_price", "unit_price", "listing_date", "last_transaction_date",
        "mortgage_info", "layout_image", "ke_code", "house_link", "city",
        "building_year", "building_structure", "data_source",
        "platform_listing_id", "created_at", "updated_at"
    )
)

# Query Parameters
class CommunityQueryParams(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    building_year: Optional[int] = None

class ErshoufangQueryParams(BaseModel):
    search_keyword: Optional[str] = Field(None, description='搜索关键词')
    city: Optional[str] = Field(None, description='城市')
    community_name: Optional[str] = Field(None, description='小区名')
    region: Optional[str] = Field(None, description='区域')
    area: Optional[str] = Field(None, description='商圈')
    layout: Optional[str] = Field(None, description='户型')
    orientation: Optional[str] = Field(None, description='朝向')
    floor: Optional[str] = Field(None, description='楼层')
    total_price_min: Optional[float] = Field(None, description='最低总价')
    total_price_max: Optional[float] = Field(None, description='最高总价')
    size_min: Optional[float] = Field(None, description='最小面积')
    size_max: Optional[float] = Field(None, description='最大面积')
    data_source: Optional[str] = Field(None, description='数据来源')
    sort_by: Optional[str] = Field(None, description='排序字段')
    sort_direction: Optional[str] = Field('desc', description='排序方向')
    page: int = Field(1, description='页码')
    page_size: int = Field(10, description='每页数量')

# DealRecord Schemas
class DealRecordBase(BaseModel):
    community_id: int = Field(..., description='小区ID')
    source: str = Field(..., description='数据来源')
    source_transaction_id: Optional[str] = Field(None, description='来源平台交易ID')
    deal_date: date = Field(..., description='成交日期')
    total_price: float = Field(..., description='成交总价')
    unit_price: float = Field(..., description='成交单价')
    layout: Optional[str] = Field(None, description='户型')
    size: Optional[float] = Field(None, description='建筑面积')
    floor_info: Optional[str] = Field(None, description='楼层信息')
    orientation: Optional[str] = Field(None, description='房屋朝向')
    building_year: Optional[int] = Field(None, description='建筑年代')
    agency: Optional[str] = Field(None, description='中介公司')
    deal_cycle: Optional[int] = Field(None, description='成交周期')
    house_link: Optional[str] = Field(None, description='房源链接')
    layout_image: Optional[str] = Field(None, description='户型图链接')
    entry_time: Optional[datetime] = Field(None, description='数据入库时间')
    original_data: Optional[dict] = Field(None, description='原始数据')

class DealRecordCreate(DealRecordBase):
    pass

class DealRecordUpdate(DealRecordBase):
    community_id: Optional[int] = None
    source: Optional[str] = None
    deal_date: Optional[date] = None
    total_price: Optional[float] = None
    unit_price: Optional[float] = None

class DealRecordInDB(DealRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Response Models
class DealRecordResponse(BaseModel):
    id: int
    community_id: int
    community_name: Optional[str] = None
    source: str
    source_transaction_id: Optional[str] = None
    deal_date: date
    total_price: float
    unit_price: float
    layout: Optional[str] = None
    size: Optional[float] = None
    floor_info: Optional[str] = None
    orientation: Optional[str] = None
    building_year: Optional[int] = None
    agency: Optional[str] = None
    deal_cycle: Optional[int] = None
    house_link: Optional[str] = None
    layout_image: Optional[str] = None
    entry_time: Optional[datetime] = None
    original_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DealRecordQueryParams(BaseModel):
    search_keyword: Optional[str] = None
    community_id: Optional[int] = None
    layout: Optional[str] = None
    floor_info: Optional[str] = None
    deal_date_start: Optional[date] = None
    deal_date_end: Optional[date] = None
    city: Optional[str] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = 'deal_date'
    sort_direction: str = 'desc'

    def __init__(self, **data):
        super().__init__(**data)
        self.search_keyword = data.get('search_keyword')
        self.community_id = data.get('community_id')
        self.layout = data.get('layout')
        self.floor_info = data.get('floor_info')
        self.deal_date_start = data.get('deal_date_start')
        self.deal_date_end = data.get('deal_date_end')
        self.city = data.get('city')
        self.page = data.get('page')
        self.page_size = data.get('page_size')
        self.sort_by = data.get('sort_by')
        self.sort_direction = data.get('sort_direction')

    def __str__(self):
        return f"DealRecordQueryParams(search_keyword={self.search_keyword}, community_id={self.community_id}, layout={self.layout}, floor_info={self.floor_info}, deal_date_start={self.deal_date_start}, deal_date_end={self.deal_date_end}, city={self.city}, page={self.page}, page_size={self.page_size}, sort_by={self.sort_by}, sort_direction={self.sort_direction})" 