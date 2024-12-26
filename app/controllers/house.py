from typing import List, Dict
from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.functions import Count
from app.models.house import Community, Ershoufang, DealRecord
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordResponse,
    DealRecordQueryParams
)
from datetime import datetime

class CommunityController:
    @staticmethod
    async def get_communities(params: CommunityQueryParams) -> Dict:
        query = Community.all()
        
        if params.name:
            query = query.filter(name__icontains=params.name)
        if params.region:
            query = query.filter(region=params.region)
        if params.area:
            query = query.filter(area=params.area)
        if params.building_year:
            query = query.filter(building_year=params.building_year)
            
        communities = await query.order_by('-created_at')
        
        # 修改返回格式，使用 data 而不是 error
        return {
            "code": 200,
            "msg": "OK",
            "data": {
                "items": [await CommunityResponse.from_tortoise_orm(community) for community in communities],
                "total": len(communities)
            }
        }

    @staticmethod
    async def create_community(data: CommunityCreate) -> Dict:
        try:
            community = await Community.create(**data.model_dump(exclude_unset=True))
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await CommunityResponse.from_tortoise_orm(community)
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_community(id: int, data: CommunityUpdate) -> Dict:
        community = await Community.get_or_none(id=id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        
        await community.update_from_dict(data.model_dump(exclude_unset=True))
        await community.save()
        return {
            "code": 200,
            "msg": "更新成功",
            "data": await CommunityResponse.from_tortoise_orm(community)
        }

    @staticmethod
    async def delete_community(id: int) -> Dict:
        community = await Community.get_or_none(id=id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")
        await community.delete()
        return {
            "code": 200,
            "msg": "删除成功",
            "data": None
        }

class ErshoufangController:
    @staticmethod
    def calculate_floor_info(location_floor: int, total_floors: int) -> str:
        """计算楼层描述
        x = 所在楼层/总层高
        x < 1/3: 低楼层
        1/3 <= x < 2/3: 中楼层
        x >= 2/3: 高楼层
        """
        try:
            # 确保输入是数字
            location_floor = int(location_floor)
            total_floors = int(total_floors)
            
            if location_floor <= 0 or total_floors <= 0:
                return None
                
            if location_floor > total_floors:
                return None
                
            ratio = location_floor / total_floors
            if ratio < 1/3:  # 修改判断条件
                return f"低楼层/共{total_floors}层"
            elif ratio < 2/3:  # 修改判断条件
                return f"中楼层/共{total_floors}层"
            else:
                return f"高楼层/共{total_floors}层"
        except (TypeError, ValueError):
            return None

    @staticmethod
    async def get_ershoufangs(params: ErshoufangQueryParams) -> Dict:
        query = Ershoufang.all().prefetch_related('community')
        
        # 搜索关键词
        if params.search_keyword:
            query = query.filter(
                Q(community_name__icontains=params.search_keyword) |
                Q(region__icontains=params.search_keyword) |
                Q(area__icontains=params.search_keyword)
            )
        
        # 基本筛选条件
        if params.city:
            query = query.filter(Q(city=params.city) | Q(city__isnull=True))
        if params.community_name:
            query = query.filter(community_name__icontains=params.community_name)
        if params.region:
            query = query.filter(region=params.region)
        if params.area:
            query = query.filter(area=params.area)
        if params.layout:
            query = query.filter(layout=params.layout)
        if params.orientation:
            query = query.filter(orientation=params.orientation)
        if params.floor:
            query = query.filter(floor__icontains=params.floor)
            
        # 范围筛选
        if params.total_price_min is not None:
            query = query.filter(total_price__gte=params.total_price_min)
        if params.total_price_max is not None:
            query = query.filter(total_price__lte=params.total_price_max)
        if params.size_min is not None:
            query = query.filter(size__gte=params.size_min)
        if params.size_max is not None:
            query = query.filter(size__lte=params.size_max)
        if params.data_source:
            query = query.filter(data_source=params.data_source)
            
        # 获取总数
        total = await query.count()
        
        # 排序
        sort_field = params.sort_by or 'created_at'
        sort_direction = params.sort_direction or 'desc'
        if sort_direction == 'desc':
            sort_field = f'-{sort_field}'
        query = query.order_by(sort_field)
        
        # 分页
        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)
        
        # 获取数据
        ershoufangs = await query

        # 格式化返回数据
        formatted_items = []
        for item in ershoufangs:
            response_data = await ErshoufangResponse.from_tortoise_orm(item)
            item_dict = response_data.model_dump()
            
            # 格式化日期
            if item_dict.get('listing_date'):
                item_dict['listing_date'] = item_dict['listing_date'].strftime('%Y-%m-%d')
            
            # 确保楼层信息存在
            if not item_dict.get('floor') and item_dict.get('floor_number') and item_dict.get('total_floors'):
                item_dict['floor'] = ErshoufangController.calculate_floor_info(
                    item_dict['floor_number'],
                    item_dict['total_floors']
                )
            
            formatted_items.append(item_dict)

        # 获取筛选选项
        filter_options = await ErshoufangController._get_filter_options()
        
        return {
            "code": 200,
            "msg": "OK",
            "data": {
                "total": total,
                "items": formatted_items,
                "filter_options": filter_options
            }
        }

    @staticmethod
    async def _get_filter_options() -> Dict:
        """获取筛选选项"""
        return {
            "regions": await Ershoufang.all().distinct().values_list('region', flat=True),
            "areas": await Ershoufang.all().distinct().values_list('area', flat=True),
            "layouts": await Ershoufang.all().distinct().values_list('layout', flat=True),
            "orientations": await Ershoufang.all().distinct().values_list('orientation', flat=True),
            "cities": await Ershoufang.all().distinct().values_list('city', flat=True)
        }

    @staticmethod
    async def create_ershoufang(data: ErshoufangCreate) -> Dict:
        try:
            # 验证小区是否存在
            community = await Community.get_or_none(id=data.community_id)
            if not community:
                raise HTTPException(status_code=404, detail="Community not found")
            
            # 准备创建数据
            create_data = data.model_dump(exclude_unset=True)
            
            # 确保设置城市字段
            if not create_data.get('city'):
                create_data['city'] = 'shanghai'  # 默认设置为上海
            
            # 计算楼层信息
            if create_data.get('floor_number') and create_data.get('total_floors'):
                floor_info = ErshoufangController.calculate_floor_info(
                    create_data['floor_number'],
                    create_data['total_floors']
                )
                if floor_info:
                    create_data['floor'] = floor_info
            
            # 计算单价
            if create_data.get('total_price') and create_data.get('size'):
                total_price = float(create_data['total_price'])
                size = float(create_data['size'])
                if size > 0:
                    create_data['unit_price'] = round(total_price * 10000 / size, 2)
            
            # 添加今日日期作为挂牌时间
            today = datetime.now()
            create_data['listing_date'] = today.strftime('%Y-%m-%d')
            
            ershoufang = await Ershoufang.create(**create_data)
            
            # 格式化返回数据
            response_data = await ErshoufangResponse.from_tortoise_orm(ershoufang)
            response_dict = response_data.model_dump()
            
            # 格式化返回的日期
            if response_dict.get('listing_date'):
                response_dict['listing_date'] = response_dict['listing_date'].strftime('%Y-%m-%d')
            
            return {
                "code": 200,
                "msg": "创建成功",
                "data": response_dict
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_ershoufang(id: int, data: ErshoufangUpdate) -> Dict:
        ershoufang = await Ershoufang.get_or_none(id=id)
        if not ershoufang:
            raise HTTPException(status_code=404, detail="Ershoufang not found")
        
        # 准备更新数据
        update_data = data.model_dump(exclude_unset=True)
        
        # 确保设置城市字段
        if not update_data.get('city'):
            update_data['city'] = 'shanghai'  # 默认设置为上海
        
        print(f"Debug - Update data received: {update_data}")  # 调试信息
        
        # 处理楼层信息
        floor_number = update_data.get('floor_number')
        total_floors = update_data.get('total_floors')
        
        # 如果提供了任一楼层信息，重新计算楼层描述
        if floor_number is not None or total_floors is not None:
            # 获取当前值或使用更新值
            current_floor_number = floor_number if floor_number is not None else ershoufang.floor_number
            current_total_floors = total_floors if total_floors is not None else ershoufang.total_floors
            
            print(f"Debug - Current floor numbers: {current_floor_number}, {current_total_floors}")  # 调试信息
            
            # 确保两个值都存在且为有效数字
            if current_floor_number is not None and current_total_floors is not None:
                try:
                    current_floor_number = int(current_floor_number)
                    current_total_floors = int(current_total_floors)
                    
                    # 更新楼层相关字段
                    update_data['floor_number'] = current_floor_number
                    update_data['total_floors'] = current_total_floors
                    
                    # 计算楼层描述
                    floor_info = ErshoufangController.calculate_floor_info(
                        current_floor_number,
                        current_total_floors
                    )
                    print(f"Debug - Calculated floor info: {floor_info}")  # 调试信息
                    
                    if floor_info:
                        update_data['floor'] = floor_info
                        print(f"Debug - Updated floor info: {update_data['floor']}")  # 调试信息
                except (TypeError, ValueError) as e:
                    print(f"Debug - Error converting floor numbers: {e}")  # 调试信息
                    pass
        
        # 计算单价
        if 'total_price' in update_data or 'size' in update_data:
            total_price = float(update_data.get('total_price', ershoufang.total_price or 0))
            size = float(update_data.get('size', ershoufang.size or 0))
            if size > 0 and total_price > 0:
                update_data['unit_price'] = round(total_price * 10000 / size, 2)
        
        # 保持原有的挂牌时间
        if 'listing_date' in update_data:
            del update_data['listing_date']
        
        # 更新数据前打印
        print(f"Debug - Final update data: {update_data}")  # 调试信息
        
        # 更新数据
        await ershoufang.update_from_dict(update_data)
        await ershoufang.save()
        
        # 更新后重新获取数据
        ershoufang = await Ershoufang.get(id=id)
        print(f"Debug - Updated ershoufang: {ershoufang}")  # 调试信息
        
        # 格式化返回数据
        response_data = await ErshoufangResponse.from_tortoise_orm(ershoufang)
        response_dict = response_data.model_dump()
        
        # 格式化返回的日期
        if response_dict.get('listing_date'):
            response_dict['listing_date'] = response_dict['listing_date'].strftime('%Y-%m-%d')
        
        return {
            "code": 200,
            "msg": "更新成功",
            "data": response_dict
        }

    @staticmethod
    async def delete_ershoufang(id: int) -> Dict:
        ershoufang = await Ershoufang.get_or_none(id=id)
        if not ershoufang:
            raise HTTPException(status_code=404, detail="Ershoufang not found")
        await ershoufang.delete()
        return {
            "code": 200,
            "msg": "删除成功",
            "data": None
        }

class DealRecordController:
    @staticmethod
    async def get_deal_records(params: DealRecordQueryParams) -> Dict:
        try:
            query = DealRecord.all().prefetch_related('community')
            
            # 添加城市筛选条件
            if params.city:
                query = query.filter(community__city=params.city)
            
            # 基本筛选条件
            if params.search_keyword:
                query = query.filter(
                    Q(community__name__icontains=params.search_keyword) |
                    Q(layout__icontains=params.search_keyword)
                )
            
            # 户型筛选 - 与在售房源保持一致
            if params.layout:
                if params.layout == 'other':
                    # 其他户型：非 1-4 室的户型
                    query = query.filter(
                        ~Q(layout__startswith='1室') &
                        ~Q(layout__startswith='2室') &
                        ~Q(layout__startswith='3室') &
                        ~Q(layout__startswith='4室')
                    )
                else:
                    # 精确匹配 1-4 室
                    query = query.filter(layout__startswith=f'{params.layout}室')

            # 楼层筛选 - 与在售房源保持一致
            if params.floor_info:
                if params.floor_info == 'low':
                    query = query.filter(floor_info__icontains='低')
                elif params.floor_info == 'middle':
                    query = query.filter(floor_info__icontains='中')
                elif params.floor_info == 'high':
                    query = query.filter(floor_info__icontains='高')

            # ... 其他代码保持不变 ...

            # 排序
            sort_field = params.sort_by
            if params.sort_direction == 'desc':
                sort_field = f"-{sort_field}"
            query = query.order_by(sort_field)
                
            # 获取总数
            total = await query.count()
                
            # 分页
            records = await query.offset((params.page - 1) * params.page_size).limit(params.page_size)
                
            # 构建响应数据，包含小区名称
            items = []
            for record in records:
                record_dict = {
                    "id": record.id,
                    "community_id": record.community_id,
                    "community_name": record.community.name if record.community else None,
                    "source": record.source,
                    "source_transaction_id": record.source_transaction_id,
                    "deal_date": record.deal_date,
                    "total_price": record.total_price,
                    "unit_price": record.unit_price,
                    "layout": record.layout,
                    "size": record.size,
                    "floor_info": record.floor_info,
                    "orientation": record.orientation,
                    "building_year": record.building_year,
                    "agency": record.agency,
                    "deal_cycle": record.deal_cycle,
                    "house_link": record.house_link,
                    "layout_image": record.layout_image,
                    "entry_time": record.entry_time,
                    "original_data": record.original_data,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at
                }
                items.append(record_dict)
                
            return {
                "code": 200,
                "msg": "OK",
                "data": {
                    "items": items,
                    "total": total,
                    "page": params.page,
                    "page_size": params.page_size
                }
            }
        except Exception as e:
            print(f"Error in get_deal_records: {str(e)}")
            return {
                "code": 500,
                "msg": "获取数据失败",
                "data": None
            }

    @staticmethod
    async def create_deal_record(data: DealRecordCreate) -> Dict:
        try:
            # 创建记录
            record = await DealRecord.create(**data.model_dump(exclude_unset=True))
            
            # 手动构建响应数据
            record_dict = {
                "id": record.id,
                "community_id": record.community_id,
                "source": record.source,
                "source_transaction_id": record.source_transaction_id,
                "deal_date": record.deal_date,
                "total_price": record.total_price,
                "unit_price": record.unit_price,
                "layout": record.layout,
                "size": record.size,
                "floor_info": record.floor_info,
                "orientation": record.orientation,
                "building_year": record.building_year,
                "agency": record.agency,
                "deal_cycle": record.deal_cycle,
                "house_link": record.house_link,
                "layout_image": record.layout_image,
                "entry_time": record.entry_time,
                "original_data": record.original_data,
                "created_at": record.created_at,
                "updated_at": record.updated_at
            }
            
            return {
                "code": 200,
                "msg": "创建成功",
                "data": record_dict
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update_deal_record(id: int, data: DealRecordUpdate) -> Dict:
        try:
            record = await DealRecord.get_or_none(id=id)
            if not record:
                raise HTTPException(status_code=404, detail="Record not found")
            
            await record.update_from_dict(data.model_dump(exclude_unset=True))
            await record.save()
            
            # 手动构建响应数据
            record_dict = {
                "id": record.id,
                "community_id": record.community_id,
                "source": record.source,
                "source_transaction_id": record.source_transaction_id,
                "deal_date": record.deal_date,
                "total_price": record.total_price,
                "unit_price": record.unit_price,
                "layout": record.layout,
                "size": record.size,
                "floor_info": record.floor_info,
                "orientation": record.orientation,
                "building_year": record.building_year,
                "agency": record.agency,
                "deal_cycle": record.deal_cycle,
                "house_link": record.house_link,
                "layout_image": record.layout_image,
                "entry_time": record.entry_time,
                "original_data": record.original_data,
                "created_at": record.created_at,
                "updated_at": record.updated_at
            }
            
            return {
                "code": 200,
                "msg": "更新成功",
                "data": record_dict
            }
        except Exception as e:
            print(f"Error in update_deal_record: {str(e)}")  # 添加错误日志
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def delete_deal_record(id: int) -> Dict:
        record = await DealRecord.get_or_none(id=id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        await record.delete()
        return {
            "code": 200,
            "msg": "删除成功",
            "data": None
        } 