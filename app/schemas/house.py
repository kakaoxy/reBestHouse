from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.house import Community, Ershoufang, DealRecord
import time
from decimal import Decimal

# Community Schemas
class CommunityBase(BaseModel):
    name: str
    city: str
    region: str
    area: str
    address: Optional[str] = None
    building_type: Optional[str] = None
    property_rights: Optional[str] = None
    total_houses: Optional[int] = Field(None, ge=0, le=100000, description='房屋总数')
    building_year: Optional[int] = Field(None, ge=1800, le=2100, description='建筑年代')

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
    total_houses: Optional[int] = Field(None, ge=0, le=100000, description='房屋总数')
    building_year: Optional[int] = Field(None, ge=1800, le=2100, description='建筑年代')

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
    size: Optional[float] = Field(None, ge=1, le=10000, description='建筑面积')
    floor: Optional[str] = Field(None, description='楼层信息')
    floor_number: Optional[int] = Field(None, ge=-10, le=150, description='所在楼层')
    total_floors: Optional[int] = Field(None, ge=1, le=150, description='总楼层')
    orientation: Optional[str] = Field(None, description='房屋朝向')
    ladder_ratio: Optional[str] = Field(None, description='梯户比')
    total_price: float = Field(..., ge=0, le=1000000000, description='房源总价')
    unit_price: Optional[float] = Field(None, ge=0, le=1000000, description='房源单价')
    listing_date: Optional[datetime] = Field(None, description='挂牌时间')
    last_transaction_date: Optional[datetime] = Field(None, description='上次交易时间')
    mortgage_info: Optional[str] = Field(None, description='抵押信息')
    layout_image: Optional[str] = Field(None, description='户型图链接')
    house_link: Optional[str] = Field(None, description='房源链接')
    city: Optional[str] = Field(None, description='城市')
    building_year: Optional[int] = Field(None, ge=1800, le=2100, description='建筑年代')
    building_structure: Optional[str] = Field(None, description='楼栋结构')
    data_source: str = Field(..., description='数据来源')
    platform_listing_id: Optional[str] = Field(None, description='来源平台房源ID')

class ErshoufangCreate(BaseModel):
    community_id: Optional[int] = None
    community_name: str
    region: str
    area: str
    layout: str
    size: float = Field(..., ge=1, le=10000)
    floor: Optional[str] = None
    floor_number: Optional[int] = Field(None, ge=-10, le=150)
    total_floors: Optional[int] = Field(None, ge=1, le=150)
    orientation: Optional[str] = None
    ladder_ratio: Optional[str] = None
    total_price: float = Field(..., ge=0, le=1000000000)
    unit_price: Optional[float] = Field(None, ge=0, le=1000000)
    listing_date: Optional[datetime] = None
    last_transaction_date: Optional[datetime] = None
    mortgage_info: Optional[str] = None
    layout_image: Optional[str] = None
    house_link: Optional[str] = None
    city: Optional[str] = None
    building_year: Optional[int] = Field(None, ge=1800, le=2100)
    building_structure: Optional[str] = None
    data_source: str = 'import'
    platform_listing_id: Optional[str] = None
    house_id: Optional[str] = None

class ErshoufangUpdate(ErshoufangBase):
    community_id: Optional[int] = Field(None, description='小区ID')
    total_price: Optional[float] = Field(None, ge=0, le=1000000000, description='房源总价')
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
        "mortgage_info", "layout_image", "house_link", "city",
        "building_year", "building_structure", "data_source",
        "platform_listing_id", "created_at", "updated_at"
    )
)

# Query Parameters
class CommunityQueryParams(BaseModel):
    city: str
    page: int = 1
    page_size: int = 10
    name: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    building_year: Optional[int] = Field(None, ge=1800, le=2100)
    search_keyword: Optional[str] = None

class ErshoufangQueryParams(BaseModel):
    page: int = 1
    page_size: int = 10
    city: Optional[str] = None
    search_keyword: Optional[str] = None
    layout: Optional[str] = None
    orientation: Optional[str] = None
    floor: Optional[str] = None
    size_min: Optional[float] = Field(None, ge=1, le=10000)
    size_max: Optional[float] = Field(None, ge=1, le=10000)
    sort_by: str = 'listing_date'
    sort_direction: str = 'desc'
    community_id: Optional[int] = None

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        self.search_keyword = data.get('search_keyword')
        self.community_id = data.get('community_id')
        self.layout = data.get('layout')
        self.orientation = data.get('orientation')
        self.floor = data.get('floor')
        self.size_min = data.get('size_min')
        self.size_max = data.get('size_max')
        self.city = data.get('city')
        self.page = data.get('page', 1)
        self.page_size = data.get('page_size', 10)
        self.sort_by = data.get('sort_by', 'listing_date')
        self.sort_direction = data.get('sort_direction', 'desc')

# DealRecord Schemas
class DealRecordBase(BaseModel):
    community_id: int
    community_name: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    size: float = Field(..., ge=1, le=10000)
    total_price: float = Field(..., ge=0, le=1000000000)
    deal_date: date
    layout: Optional[str] = None
    floor_number: Optional[int] = Field(None, ge=-10, le=150)
    total_floors: Optional[int] = Field(None, ge=1, le=150)
    floor_info: Optional[str] = None
    orientation: Optional[str] = None
    unit_price: Optional[float] = Field(None, ge=0, le=1000000)
    deal_cycle: Optional[int] = Field(None, ge=0, le=3650)
    agency: Optional[str] = None
    source: Optional[str] = 'store'
    tags: Optional[str] = None
    layout_url: Optional[str] = None
    house_url: Optional[str] = None
    building_year: Optional[int] = Field(None, ge=1800, le=2100)
    decoration: Optional[str] = None
    building_structure: Optional[str] = None
    platform_house_id: Optional[str] = None

    @validator('deal_date', pre=True)
    def validate_deal_date(cls, v):
        if isinstance(v, (date, datetime)):
            return v.date() if isinstance(v, datetime) else v
        
        if isinstance(v, (int, float)):
            try:
                # 处理时间戳（秒）
                if len(str(int(v))) <= 10:
                    return datetime.fromtimestamp(v).date()
                # 处理时间戳（毫秒）
                return datetime.fromtimestamp(v / 1000).date()
            except (ValueError, OSError):
                raise ValueError('Invalid timestamp')
        
        if isinstance(v, str):
            try:
                # 尝试解析 ISO 格式日期
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                try:
                    # 尝试解析时间戳字符串
                    ts = float(v)
                    if len(str(int(ts))) <= 10:
                        return datetime.fromtimestamp(ts).date()
                    return datetime.fromtimestamp(ts / 1000).date()
                except (ValueError, OSError):
                    raise ValueError('Invalid date format. Expected YYYY-MM-DD or timestamp')
        
        raise ValueError('Invalid date format')

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }

class DealRecordCreate(DealRecordBase):
    pass

class DealRecordUpdate(DealRecordBase):
    community_id: Optional[int] = None
    size: Optional[float] = Field(None, ge=1, le=10000)
    total_price: Optional[float] = Field(None, ge=0, le=1000000000)
    deal_date: Optional[date] = None

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }

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
    region: Optional[str] = None
    area: Optional[str] = None
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

class OpportunityBase(BaseModel):
    community_id: int
    community_name: Optional[str] = None
    layout: Optional[str] = None
    floor: Optional[str] = None
    area: Optional[float] = Field(None, ge=1, le=10000)
    total_price: Optional[float] = Field(None, ge=0, le=1000000000)
    unit_price: Optional[float] = Field(None, ge=0, le=1000000)
    address: Optional[str] = None
    building_number: Optional[str] = None
    room_number: Optional[str] = None
    is_full_five: Optional[bool] = False
    is_full_two: Optional[bool] = False
    is_unique: Optional[bool] = False
    transaction_source: Optional[str] = None
    layout_image: Optional[str] = None
    interior_image: Optional[str] = None
    location_image: Optional[str] = None
    opportunity_owner: Optional[str] = None
    belonging_owner: Optional[str] = None
    status: str = '待评估'
    remarks: Optional[str] = None
    ershoufang_id: Optional[int] = None

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityUpdate(OpportunityBase):
    pass

class OpportunityQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    city: Optional[str] = None
    community_name: Optional[str] = None
    status: Optional[str] = None 

class OpportunityFollowUpCreate(BaseModel):
    opportunity_id: int = Field(..., description='商机ID')
    follow_up_time: datetime = Field(..., description='跟进时间')
    follow_up_method: str = Field(..., description='跟进方式')
    follow_up_content: str = Field(..., description='跟进内容')
    authorized_price: Optional[float] = Field(None, ge=0, le=1000000000, description='本次授权价格')
    price_adjusted: bool = Field(default=False, description='价格是否调整')
    adjust_reason: Optional[str] = Field(None, description='价格调整原因')
    follow_up_result: str = Field(..., description='跟进结果')

class OpportunityFollowUpResponse(BaseModel):
    id: int
    opportunity_id: int
    follow_up_time: datetime  
    follow_up_method: str
    follow_up_content: str
    authorized_price: Optional[float]
    price_adjusted: bool
    adjust_reason: Optional[str]
    follow_up_result: str
    user_id: int
    user_name: str
    created_at: datetime
    updated_at: datetime 

class ProjectBase(BaseModel):
    opportunity_id: int
    address: str
    contract_price: Decimal = Field(..., ge=0, le=1000000000)
    contract_period: int = Field(..., ge=1, le=3650)
    signer: str
    delivery_date: datetime
    current_phase: Optional[str] = None

class ProjectCreate(BaseModel):
    opportunity_id: int
    address: str
    contract_price: Decimal = Field(..., ge=0, le=1000000000)
    contract_period: int = Field(..., ge=1, le=3650)
    signer: str
    delivery_date: Optional[datetime]
    current_phase: str = 'delivery'
    decoration_company: Optional[str] = None

class ProjectUpdate(BaseModel):
    address: Optional[str] = None
    contract_price: Optional[Decimal] = Field(None, ge=0, le=1000000000)
    contract_period: Optional[int] = Field(None, ge=1, le=3650)
    signer: Optional[str] = None
    delivery_date: Optional[datetime] = None
    current_phase: Optional[str] = None
    decoration_company: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ProjectQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    opportunity_id: Optional[int] = None
    current_phase: Optional[str] = None
    signer: Optional[str] = None
    delivery_date_start: Optional[date] = None
    delivery_date_end: Optional[date] = None
    city: Optional[str] = None  # 添加城市筛选字段

class ConstructionPhaseBase(BaseModel):
    project_id: int
    phase_type: str
    responsible: str
    notes: Optional[str] = None
    complete_time: Optional[datetime] = None

class ConstructionPhaseCreate(ConstructionPhaseBase):
    pass

class ConstructionPhaseUpdate(BaseModel):
    phase_type: Optional[str] = None
    responsible: Optional[str] = None
    notes: Optional[str] = None
    complete_time: Optional[datetime] = None

class ConstructionPhaseResponse(ConstructionPhaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ConstructionPhaseQueryParams(BaseModel):
    page: int = 1
    page_size: int = 20
    project_id: Optional[int] = None
    phase_type: Optional[str] = None
    responsible: Optional[str] = None
    is_completed: Optional[bool] = None

class PhaseMaterialBase(BaseModel):
    phase_id: int
    material_type: str
    file_path: str
    uploader: str

class PhaseMaterialCreate(PhaseMaterialBase):
    pass

class PhaseMaterialResponse(PhaseMaterialBase):
    id: int
    upload_time: datetime 