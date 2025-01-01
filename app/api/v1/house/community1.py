from typing import Optional
from fastapi import APIRouter, Query
from app.models import Community
from app.schemas.base import BaseResp
from app.schemas.house import CommunityCreate, CommunityUpdate, CommunityList
from tortoise.expressions import Q

router = APIRouter()

@router.get("", response_model=BaseResp[CommunityList])
async def get_communities(
    city: Optional[str] = None,
    search_keyword: Optional[str] = None,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0),
):
    """获取小区列表"""
    # 基础查询
    query = Community.all()
    
    # 严格按城市筛选
    if city:
        # 使用精确匹配，转换为小写
        city = city.lower()
        query = query.filter(city=city)
        print(f"Filtering by city: {city}")
    else:
        # 如果没有指定城市，默认使用上海
        query = query.filter(city='shanghai')
    
    # 添加关键词搜索
    if search_keyword:
        query = query.filter(
            Q(name__icontains=search_keyword) |
            Q(region__icontains=search_keyword) |
            Q(area__icontains=search_keyword)
        )
    
    # 计算总数
    total = await query.count()
    
    # 分页查询
    items = await query.offset((page - 1) * page_size).limit(page_size)
    
    # 转换为响应格式
    items_data = [
        {
            "id": item.id,
            "name": item.name,
            "city": item.city,
            "region": item.region,
            "area": item.area,
            "address": item.address,
            "building_type": item.building_type,
            "property_rights": item.property_rights,
            "total_houses": item.total_houses,
            "building_year": item.building_year
        }
        for item in items
    ]
    
    return BaseResp(
        code=200,
        msg="success",
        data={
            "items": items_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )

@router.post("", response_model=BaseResp)
async def create_community(community: CommunityCreate):
    """创建小区"""
    # 确保城市值是小写的
    data = community.model_dump()
    if data.get('city'):
        data['city'] = data['city'].lower()
    
    await Community.create(**data)
    return BaseResp(code=200, msg="创建成功")

@router.put("/{id}", response_model=BaseResp)
async def update_community(id: int, community: CommunityUpdate):
    """更新小区"""
    # 确保城市值是小写的
    data = community.model_dump(exclude_unset=True)
    if data.get('city'):
        data['city'] = data['city'].lower()
    
    await Community.filter(id=id).update(**data)
    return BaseResp(code=200, msg="更新成功")

# ... 其他路由保持不变 ... 