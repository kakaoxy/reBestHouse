from typing import List, Dict
from fastapi import APIRouter, Depends
from app.controllers.house import community_controller, ershoufang_controller, deal_record_controller, opportunity_controller
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordQueryParams,
    OpportunityQueryParams, OpportunityCreate, OpportunityUpdate
)
from app.core.dependency import DependPermisson

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
    return await community_controller.create_community(data)

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
    return await opportunity_controller.create_opportunity(data)

@router.put(
    "/opportunities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新商机"
)
async def update_opportunity(id: int, data: OpportunityUpdate):
    return await opportunity_controller.update_opportunity(id, data)

@router.delete(
    "/opportunities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除商机"
)
async def delete_opportunity(id: int):
    return await opportunity_controller.delete_opportunity(id) 