from typing import List, Dict
from fastapi import APIRouter, Depends
from app.controllers.house import CommunityController, ErshoufangController, DealRecordController
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordQueryParams
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
    return await CommunityController.get_communities(params)

@router.post(
    "/communities",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建小区"
)
async def create_community(data: CommunityCreate):
    return await CommunityController.create_community(data)

@router.put(
    "/communities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新小区"
)
async def update_community(id: int, data: CommunityUpdate):
    return await CommunityController.update_community(id, data)

@router.delete(
    "/communities/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除小区"
)
async def delete_community(id: int):
    return await CommunityController.delete_community(id)

# Ershoufang routes
@router.get(
    "/ershoufangs",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取二手房列表"
)
async def get_ershoufangs(params: ErshoufangQueryParams = Depends()):
    return await ErshoufangController.get_ershoufangs(params)

@router.post(
    "/ershoufangs",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建二手房"
)
async def create_ershoufang(data: ErshoufangCreate):
    return await ErshoufangController.create_ershoufang(data)

@router.put(
    "/ershoufangs/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新二手房"
)
async def update_ershoufang(id: int, data: ErshoufangUpdate):
    return await ErshoufangController.update_ershoufang(id, data)

@router.delete(
    "/ershoufangs/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除二手房"
)
async def delete_ershoufang(id: int):
    return await ErshoufangController.delete_ershoufang(id)

# DealRecord routes
@router.get(
    "/deal-records",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="获取成交记录列表"
)
async def get_deal_records(params: DealRecordQueryParams = Depends()):
    return await DealRecordController.get_deal_records(params)

@router.post(
    "/deal-records",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="创建成交记录"
)
async def create_deal_record(data: DealRecordCreate):
    return await DealRecordController.create_deal_record(data)

@router.put(
    "/deal-records/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="更新成交记录"
)
async def update_deal_record(id: int, data: DealRecordUpdate):
    return await DealRecordController.update_deal_record(id, data)

@router.delete(
    "/deal-records/{id}",
    response_model=Dict,
    dependencies=[DependPermisson],
    summary="删除成交记录"
)
async def delete_deal_record(id: int):
    return await DealRecordController.delete_deal_record(id) 