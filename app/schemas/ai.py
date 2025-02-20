from pydantic import BaseModel, Field
from typing import Optional

class AIReportRequest(BaseModel):
    community_name: str = Field(..., description='小区名称')
    layout: Optional[str] = Field(None, description='户型')
    floor: Optional[str] = Field(None, description='楼层')
    area: Optional[float] = Field(None, ge=1, le=10000, description='面积')
    total_price: Optional[float] = Field(None, ge=0, le=1000000000, description='总价')
    listing_count: int = Field(..., ge=0, description='在售房源数')
    deal_count: int = Field(..., ge=0, description='成交数量')