from typing import List, Dict
from fastapi import APIRouter, Depends, File, UploadFile, Query, Form, HTTPException
from app.controllers.house import community_controller, ershoufang_controller, deal_record_controller, opportunity_controller, opportunity_follow_up_controller
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordQueryParams,
    OpportunityQueryParams, OpportunityCreate, OpportunityUpdate,
    OpportunityFollowUpCreate
)
from app.core.dependency import DependPermisson, DependAuth
from app.models import User
from fastapi.responses import FileResponse
import os
import uuid

router = APIRouter()

# Community routes
@router.get(
    "/communities",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取小区列表"
)
async def get_communities(params: CommunityQueryParams = Depends()):
    return await community_controller.get_communities(params)

@router.post(
    "/communities",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建小区"
)
async def create_community(data: CommunityCreate):
    return await community_controller.create(data)

@router.put(
    "/communities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新小区"
)
async def update_community(id: int, data: CommunityUpdate):
    return await community_controller.update_community(id, data)

@router.delete(
    "/communities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除小区"
)
async def delete_community(id: int):
    return await community_controller.delete_community(id)

@router.post(
    "/communities/import",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="批量导入小区"
)
async def import_communities(
    file: UploadFile = File(..., description="Excel文件"),
    city: str = Form(..., description="城市")
):
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            "code": 422,
            "msg": "只支持 Excel 文件格式 (.xlsx, .xls)"
        }
    
    return await community_controller.import_communities(file, city)

# Ershoufang routes
@router.get(
    "/ershoufangs",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取二手房列表"
)
async def get_ershoufangs(params: ErshoufangQueryParams = Depends()):
    return await ershoufang_controller.get_ershoufangs(params)

@router.post(
    "/ershoufangs",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建二手房"
)
async def create_ershoufang(data: ErshoufangCreate):
    return await ershoufang_controller.create_ershoufang(data)

@router.put(
    "/ershoufangs/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新二手房"
)
async def update_ershoufang(id: int, data: ErshoufangUpdate):
    return await ershoufang_controller.update_ershoufang(id, data)

@router.delete(
    "/ershoufangs/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除二手房"
)
async def delete_ershoufang(id: int):
    return await ershoufang_controller.delete_ershoufang(id)

@router.post(
    "/ershoufangs/import",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="批量导入二手房"
)
async def import_ershoufangs(
    file: UploadFile = File(..., description="Excel文件"),
    city: str = Form(..., description="城市")
):
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            "code": 422,
            "msg": "只支持 Excel 文件格式 (.xlsx, .xls)"
        }
    
    return await ershoufang_controller.import_ershoufangs(file, city)

# DealRecord routes
@router.get(
    "/deal-records",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取成交记录列表"
)
async def get_deal_records(params: DealRecordQueryParams = Depends()):
    return await deal_record_controller.get_deal_records(params)

@router.post(
    "/deal-records",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建成交记录"
)
async def create_deal_record(data: DealRecordCreate):
    return await deal_record_controller.create_deal_record(data)

@router.put(
    "/deal-records/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新成交记录"
)
async def update_deal_record(id: int, data: DealRecordUpdate):
    return await deal_record_controller.update_deal_record(id, data)

@router.delete(
    "/deal-records/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除成交记录"
)
async def delete_deal_record(id: int):
    return await deal_record_controller.delete_deal_record(id)

@router.post(
    "/deal-records/import",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="批量导入成交记录"
)
async def import_deal_records(
    file: UploadFile = File(..., description="Excel文件"),
    city: str = Form(..., description="城市")
):
    # 验证文件类型
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            "code": 422,
            "msg": "只支持 Excel 文件格式 (.xlsx, .xls)"
        }
    
    return await deal_record_controller.import_deal_records(file, city)

@router.get(
        "/deal-records/template",
        summary="获取成交记录导入模板",
        dependencies=[DependPermisson]
)
async def get_import_template():
    """获取成交记录导入模板"""
    template_path = "templates/deal_record_import_template.xlsx"
    if not os.path.exists(template_path):
        raise HTTPException(status_code=404, detail="Template file not found")
    return FileResponse(
        template_path,
        filename="成交记录导入模板.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Opportunity routes
@router.get(
    "/opportunities",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取商机列表"
)
async def get_opportunities(params: OpportunityQueryParams = Depends()):
    return await opportunity_controller.get_opportunities(params)

@router.get(
    "/opportunities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取商机详情"
)
async def get_opportunity(id: int):
    return await opportunity_controller.get_opportunity(id)

@router.post(
    "/opportunities",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建商机"
)
async def create_opportunity(data: OpportunityCreate):
    print(f"创建商机请求数据: {data.dict()}")
    return await opportunity_controller.create_opportunity(data)

@router.put(
    "/opportunities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新商机"
)
async def update_opportunity(id: int, data: OpportunityUpdate):
    print(f"更新商机请求数据: id={id}, data={data.dict()}")
    return await opportunity_controller.update_opportunity(id, data)

@router.delete(
    "/opportunities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除商机"
)
async def delete_opportunity(id: int):
    return await opportunity_controller.delete_opportunity(id)

@router.post(
    "/opportunity/follow_up/create",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建跟进记录"
)
async def create_follow_up(
    data: OpportunityFollowUpCreate,
    current_user: User = DependAuth
):
    """创建跟进记录"""
    return await opportunity_follow_up_controller.create_follow_up(data, current_user.id)

@router.get(
    "/opportunity/{opportunity_id}/follow_ups",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取商机的跟进记录"
)
async def get_follow_ups(opportunity_id: int):
    """获取商机的所有跟进记录"""
    return await opportunity_follow_up_controller.get_follow_ups(opportunity_id)

@router.post(
    "/upload/image",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="上传图片"
)
async def upload_image(file: UploadFile = File(...)):
    """上传图片"""
    print(f"接收到图片上传请求: {file.filename}")
    
    # 检查文件类型
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="只能上传图片文件")
    
    # 生成文件名
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    print(f"生成的文件名: {filename}")
    
    # 确保上传目录存在
    upload_dir = os.path.join("static", "uploads", "images")
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, filename)
    print(f"保存路径: {file_path}")
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 返回不带 /api 前缀的 URL
    url = f"/static/uploads/images/{filename}"
    print(f"返回的URL: {url}")
    
    return {
        "code": 200,
        "msg": "上传成功",
        "data": {
            "url": url
        }
    } 