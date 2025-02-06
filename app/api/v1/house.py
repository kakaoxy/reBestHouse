from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Query, Form, HTTPException
from app.controllers.house import community_controller, ershoufang_controller, deal_record_controller, opportunity_controller, opportunity_follow_up_controller, project_controller, construction_phase_controller, phase_material_controller
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordQueryParams,
    OpportunityQueryParams, OpportunityCreate, OpportunityUpdate,
    OpportunityFollowUpCreate,
    ProjectCreate,
    ProjectUpdate,
    ProjectQueryParams,
    ConstructionPhaseCreate,
    ConstructionPhaseUpdate,
    ConstructionPhaseQueryParams
)
from app.core.dependency import DependPermisson, DependAuth
from app.models import User, Opportunity, ConstructionPhase, PhaseMaterial
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime, timedelta

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

# Project routes
@router.post(
    "/projects",
    dependencies=[DependPermisson],
    summary="创建项目"
)
async def create_project(data: ProjectCreate):
    """创建项目"""
    print("接收到的创建项目请求数据:", data.dict())
    
    # 获取关联的商机信息
    opportunity = await Opportunity.get_or_none(id=data.opportunity_id)
    if not opportunity:
        print(f"未找到ID为 {data.opportunity_id} 的商机")
        raise HTTPException(status_code=404, detail="商机不存在")
    
    print("关联的商机信息:", await opportunity.to_dict())
    
    try:
        # 创建项目时自动设置小区名称（增加空值处理）
        project_data = {
            'opportunity_id': data.opportunity_id,
            'community_name': opportunity.community_name or "",  # 确保不为空
            'address': data.address,
            'contract_price': float(data.contract_price),  # 转换为float类型
            'contract_period': data.contract_period,
            'signer': data.signer,
            'delivery_date': data.delivery_date,
            'current_phase': data.current_phase,
            'decoration_company': data.decoration_company   # 新增字段
        }
        print("准备创建的项目数据:", project_data)
        
        result = await project_controller.create_project(project_data)
        print("项目创建结果:", result)
        return result
    except Exception as e:
        print("创建项目时发生错误:", str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/projects",
    dependencies=[DependPermisson],
    summary="获取项目列表"
)
async def get_projects(
    page: int = 1,
    page_size: int = 20,
    opportunity_id: Optional[int] = None,
    current_phase: Optional[str] = None,
    signer: Optional[str] = None,
    delivery_date_start: Optional[str] = None,
    delivery_date_end: Optional[str] = None
):
    """获取项目列表，支持分页和筛选"""
    params = ProjectQueryParams(
        page=page,
        page_size=page_size,
        opportunity_id=opportunity_id,
        current_phase=current_phase,
        signer=signer,
        delivery_date_start=datetime.strptime(delivery_date_start, '%Y-%m-%d').date() if delivery_date_start else None,
        delivery_date_end=datetime.strptime(delivery_date_end, '%Y-%m-%d').date() if delivery_date_end else None
    )
    return await project_controller.get_projects(params)

@router.get(
    "/projects/{project_id}",
    dependencies=[DependPermisson],
    summary="获取项目详情"
)
async def get_project_detail(project_id: int):
    """获取项目详情，包括施工阶段和材料信息"""
    return await project_controller.get_project_details(project_id)

@router.put(
    "/projects/{project_id}",
    dependencies=[DependPermisson],
    summary="更新项目信息"
)
async def update_project(project_id: int, data: ProjectUpdate):
    """
    更新项目信息
    - 可更新：地址、签约价格、签约周期、签约人、交房日期、当前阶段
    """
    # 计算销售截止日期
    if data.delivery_date:
        data.sale_deadline = data.delivery_date - timedelta(days=data.contract_period)
    return await project_controller.update(project_id, data)

@router.delete(
    "/projects/{project_id}",
    dependencies=[DependPermisson],
    summary="删除项目"
)
async def delete_project(project_id: int):
    """删除项目及其关联的施工阶段和材料信息"""
    return await project_controller.remove(project_id)

@router.get(
    "/projects/{project_id}/phases",
    dependencies=[DependPermisson],
    summary="获取项目施工阶段列表"
)
async def get_project_phases(project_id: int):
    """
    获取项目的施工阶段列表
    - project_id: 项目ID
    """
    try:
        phases = await ConstructionPhase.filter(project_id=project_id).order_by("-complete_time")
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [await phase.to_dict() for phase in phases]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/projects/phases/{phase_id}/materials",
    dependencies=[DependPermisson],
    summary="获取施工阶段材料列表"
)
async def get_phase_materials(phase_id: int):
    """
    获取施工阶段的材料列表
    - phase_id: 施工阶段ID
    """
    try:
        materials = await PhaseMaterial.filter(phase_id=phase_id).order_by("-created_at")
        return {
            "code": 200,
            "msg": "获取成功",
            "data": [await material.to_dict() for material in materials]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Construction phase routes
@router.post(
    "/construction-phases",
    dependencies=[DependPermisson],
    summary="创建施工阶段"
)
async def create_construction_phase(data: ConstructionPhaseCreate):
    """
    创建施工阶段
    - project_id: 关联的项目ID
    - phase_type: 阶段类型
    - responsible: 负责人
    - notes: 备注
    """
    return await construction_phase_controller.create_phase(data)

@router.get(
    "/construction-phases",
    dependencies=[DependPermisson],
    summary="获取施工阶段列表"
)
async def get_construction_phases(
    page: int = 1,
    page_size: int = 20,
    project_id: Optional[int] = None,
    phase_type: Optional[str] = None,
    responsible: Optional[str] = None,
    is_completed: Optional[bool] = None
):
    """获取施工阶段列表，支持分页和筛选"""
    params = ConstructionPhaseQueryParams(
        page=page,
        page_size=page_size,
        project_id=project_id,
        phase_type=phase_type,
        responsible=responsible,
        is_completed=is_completed
    )
    return await construction_phase_controller.get_phases(params)

@router.put(
    "/construction-phases/{phase_id}",
    dependencies=[DependPermisson],
    summary="更新施工阶段"
)
async def update_construction_phase(phase_id: int, data: ConstructionPhaseUpdate):
    """
    更新施工阶段
    - 可更新：阶段类型、负责人、备注、完成时间
    """
    return await construction_phase_controller.update(phase_id, data)

@router.post(
    "/construction-phases/{phase_id}/materials",
    dependencies=[DependPermisson],
    summary="上传阶段材料"
)
async def upload_phase_material(
    phase_id: int,
    file: UploadFile = File(...),
    material_type: str = Form(...),
    uploader: str = Form(...)
):
    """
    上传阶段材料
    - phase_id: 施工阶段ID
    - file: 上传的文件
    - material_type: 材料类型
    - uploader: 上传人
    """
    return await phase_material_controller.upload_phase_material(
        phase_id=phase_id,
        file=file,
        material_type=material_type,
        uploader=uploader
    ) 