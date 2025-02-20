from pydantic import BaseModel, Field

class AIReportRequest(BaseModel):
    """AI报告请求模型"""
    opportunity_id: int = Field(..., description='商机ID')