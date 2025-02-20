from fastapi import APIRouter, HTTPException, Depends
from app.controllers.ai import ai_report_controller
from app.schemas.ai import AIReportRequest
from app.core.dependency import DependPermisson
from typing import Dict

router = APIRouter()

@router.post(
    "/report/generate",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="生成AI分析报告"
)
async def generate_report(data: AIReportRequest):
    """
    生成房产投资分析AI报告
    """
    try:
        return await ai_report_controller.generate_report(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))