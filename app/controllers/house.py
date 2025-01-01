from typing import List, Dict
from fastapi import HTTPException, UploadFile
from tortoise.expressions import Q
from tortoise.functions import Count
from app.models.house import Community, Ershoufang, DealRecord, Opportunity
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordResponse,
    DealRecordQueryParams,
    OpportunityCreate, OpportunityUpdate, OpportunityQueryParams
)
from datetime import datetime
from app.core.crud import CRUDBase
import pandas as pd
from io import BytesIO

class CommunityController(CRUDBase[Community, CommunityCreate, CommunityUpdate]):
    def __init__(self):
        super().__init__(model=Community)
    
    async def get_communities(self, params: CommunityQueryParams) -> Dict:
        query = Q()
        if params.city:
            query &= Q(city=params.city.lower())
        if params.name:
            query &= Q(name__icontains=params.name)
        if params.region:
            query &= Q(region=params.region)
        if params.area:
            query &= Q(area=params.area)
        if params.building_year:
            query &= Q(building_year=params.building_year)
        if params.search_keyword:
            query &= (
                Q(name__icontains=params.search_keyword) |
                Q(region__icontains=params.search_keyword) |
                Q(area__icontains=params.search_keyword)
            )
            
        total, items = await self.list(
            page=params.page,
            page_size=params.page_size,
            search=query,
            order=["-created_at"]
        )
        
        return {
            "code": 200,
            "msg": "OK",
            "data": {
                "items": [await CommunityResponse.from_tortoise_orm(item) for item in items],
                "total": total,
                "page": params.page,
                "page_size": params.page_size
            }
        }

    async def check_duplicate(self, name: str, region: str, area: str, city: str) -> bool:
        """检查小区是否重复"""
        exists = await self.model.filter(
            name=name,
            region=region,
            area=area,
            city=city
        ).exists()
        return exists

    async def create(self, data: CommunityCreate) -> Dict:
        """创建小区前检查是否重复"""
        # 检查是否存在重复小区
        exists = await self.check_duplicate(
            name=data.name,
            region=data.region,
            area=data.area,
            city=data.city
        )
        
        if exists:
            return {
                "code": 400,
                "msg": f"小区已存在：{data.region} {data.area} {data.name}"
            }
        
        try:
            community = await self.model.create(**data.dict())
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await CommunityResponse.from_tortoise_orm(community)
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": f"创建失败：{str(e)}"
            }

    async def update_community(self, id: int, data: CommunityUpdate) -> Dict:
        try:
            community = await self.update(id, data)
            return {
                "code": 200,
                "msg": "更新成功",
                "data": await CommunityResponse.from_tortoise_orm(community)
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail="Community not found")

    async def delete_community(self, id: int) -> Dict:
        try:
            await self.remove(id)
            return {
                "code": 200,
                "msg": "删除成功",
                "data": None
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail="Community not found")

    async def import_communities(self, file: UploadFile, city: str) -> Dict:
        try:
            # 读取文件内容
            contents = await file.read()
            
            # 读取 Excel 文件
            df = pd.read_excel(BytesIO(contents))
            
            # 处理列名，移除星号
            df.columns = df.columns.str.replace('*', '').str.strip()
            
            # 清理数据 - 去除前后空格
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            # 验证必要的列
            required_columns = ['name', 'region', 'area']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "code": 400,
                    "msg": f"缺少必要的列: {', '.join(missing_columns)}"
                }
            
            # 准备导入数据
            success_count = 0
            error_list = []
            
            for _, row in df.iterrows():
                try:
                    # 检查数据有效性
                    if pd.isna(row['name']) or pd.isna(row['region']) or pd.isna(row['area']):
                        error_list.append({
                            "name": row.get('name', '未知'),
                            "error": "必填字段不能为空"
                        })
                        continue
                    
                    # 检查是否存在重复小区
                    exists = await self.check_duplicate(
                        name=row['name'],
                        region=row['region'],
                        area=row['area'],
                        city=city
                    )
                    
                    if exists:
                        error_list.append({
                            "name": row['name'],
                            "error": f"小区已存在：{row['region']} {row['area']} {row['name']}"
                        })
                        continue
                    
                    # 安全地转换数值类型
                    def safe_int_convert(value):
                        try:
                            if pd.isna(value):
                                return None
                            # 移除非数字字符
                            cleaned = str(value).strip().split()[0]
                            return int(cleaned)
                        except (ValueError, TypeError, IndexError):
                            return None
                    
                    # 准备数据
                    community_data = {
                        "name": row['name'],
                        "region": row['region'],
                        "area": row['area'],
                        "city": city.lower(),  # 强制使用当前选择的城市
                        "building_type": row.get('building_type'),
                        "property_rights": row.get('property_rights'),
                        "total_houses": safe_int_convert(row.get('total_houses')),
                        "building_year": safe_int_convert(row.get('building_year')),
                        "address": row.get('address')
                    }
                    
                    # 如果 Excel 中有 city 列，给出警告但仍使用当前选择的城市
                    if 'city' in df.columns and pd.notna(row.get('city')) and row.get('city').lower() != city.lower():
                        error_list.append({
                            "name": row['name'],
                            "error": f"Excel中的城市({row.get('city')})与当前选择的城市({city})不一致，将使用当前选择的城市"
                        })
                    
                    # 创建小区
                    await self.model.create(**community_data)
                    success_count += 1
                    
                except Exception as e:
                    error_list.append({
                        "name": row['name'],
                        "error": str(e)
                    })
            
            return {
                "code": 200,
                "msg": f"导入完成: 成功 {success_count} 条，失败 {len(error_list)} 条",
                "data": {
                    "success_count": success_count,
                    "error_count": len(error_list),
                    "errors": error_list
                }
            }
            
        except Exception as e:
            return {
                "code": 500,
                "msg": f"导入失败：{str(e)}"
            }

community_controller = CommunityController()

class ErshoufangController(CRUDBase[Ershoufang, ErshoufangCreate, ErshoufangUpdate]):
    def __init__(self):
        super().__init__(model=Ershoufang)

    def calculate_floor_info(self, location_floor: int, total_floors: int) -> str:
        """计算楼层描述
        x = 所在楼层/总层高
        x < 1/3: 低楼层
        1/3 <= x < 2/3: 中楼层
        x >= 2/3: 高楼层
        """
        try:
            location_floor = int(location_floor)
            total_floors = int(total_floors)
            
            if location_floor <= 0 or total_floors <= 0:
                return None
                
            if location_floor > total_floors:
                return None
                
            ratio = location_floor / total_floors
            if ratio < 1/3:
                return f"低楼层/共{total_floors}层"
            elif ratio < 2/3:
                return f"中楼层/共{total_floors}层"
            else:
                return f"高楼层/共{total_floors}层"
        except (TypeError, ValueError):
            return None

    async def get_ershoufangs(self, params: ErshoufangQueryParams) -> Dict:
        try:
            print(f"Received query params: {params}")  # 添加调试日志
            query = Q()
            
            # 城市筛选
            if params.city:
                query &= Q(city=params.city.lower())
            
            # 关键词搜索
            if params.search_keyword:
                query &= (
                    Q(community_name__icontains=params.search_keyword) |
                    Q(community__name__icontains=params.search_keyword)
                )
            
            # 户型筛选
            if params.layout:
                query &= Q(layout=params.layout)
            
            # 朝向筛选
            if params.orientation:
                query &= Q(orientation=params.orientation)
            
            # 楼层筛选
            if params.floor:
                query &= Q(floor__icontains=params.floor)
            
            # 面积范围筛选
            if params.size_min is not None:
                query &= Q(size__gte=params.size_min)
            if params.size_max is not None:
                query &= Q(size__lte=params.size_max)
            
            print(f"Final query conditions: {query}")  # 添加调试日志
            
            # 添加排序参数
            order_by = f"{'-' if params.sort_direction == 'desc' else ''}{params.sort_by}"
            
            # 确保关联查询小区信息
            items = await self.model.filter(query)\
                .prefetch_related('community')\
                .order_by(order_by)\
                .offset((params.page - 1) * params.page_size)\
                .limit(params.page_size)
            
            # 处理返回数据
            result_items = []
            for item in items:
                try:
                    item_dict = await item.to_dict()
                    if item.community:
                        item_dict.update({
                            'community_name': item.community.name,
                            'community_id': item.community.id,
                            'region': item.community.region,
                            'area': item.community.area
                        })
                    result_items.append(item_dict)
                except Exception as e:
                    print(f"Error processing item {item.id}: {str(e)}")
                    continue
            
            total = await self.model.filter(query).count()
            print(f"Total results: {total}")  # 添加调试日志
            
            return {
                "code": 200,
                "data": {
                    "items": result_items,
                    "total": total
                }
            }
        except Exception as e:
            print(f"Error in get_ershoufangs: {str(e)}")  # 添加错误日志
            return {
                "code": 500,
                "msg": "获取数据失败",
                "error": {
                    "message": str(e),
                    "type": type(e).__name__
                }
            }

    async def _get_filter_options(self) -> Dict:
        """获取筛选选项"""
        return {
            "regions": await self.model.all().distinct().values_list('region', flat=True),
            "areas": await self.model.all().distinct().values_list('area', flat=True),
            "layouts": await self.model.all().distinct().values_list('layout', flat=True),
            "orientations": await self.model.all().distinct().values_list('orientation', flat=True),
            "cities": await self.model.all().distinct().values_list('city', flat=True)
        }

    async def create_ershoufang(self, data: ErshoufangCreate) -> Dict:
        try:
            # 验证小区是否存在
            community = await Community.get_or_none(id=data.community_id)
            if not community:
                raise HTTPException(status_code=404, detail="Community not found")
            
            # 准备创建数据
            create_data = data.model_dump(exclude_unset=True)
            
            # 添加小区相关信息
            create_data['community_name'] = community.name
            create_data['region'] = community.region
            create_data['area'] = community.area
            
            # 确保设置城市字段
            if not create_data.get('city'):
                create_data['city'] = 'shanghai'
            
            # 计算楼层信息
            if create_data.get('floor_number') and create_data.get('total_floors'):
                floor_info = self.calculate_floor_info(
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
            create_data['listing_date'] = datetime.now().strftime('%Y-%m-%d')
            
            ershoufang = await self.create(create_data)
            
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

    async def update_ershoufang(self, id: int, data: ErshoufangUpdate) -> Dict:
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
                    floor_info = self.calculate_floor_info(
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

    async def delete_ershoufang(self, id: int) -> Dict:
        ershoufang = await Ershoufang.get_or_none(id=id)
        if not ershoufang:
            raise HTTPException(status_code=404, detail="Ershoufang not found")
        await ershoufang.delete()
        return {
            "code": 200,
            "msg": "删除成功",
            "data": None
        }

ershoufang_controller = ErshoufangController()

class DealRecordController(CRUDBase[DealRecord, DealRecordCreate, DealRecordUpdate]):
    def __init__(self):
        super().__init__(model=DealRecord)

    async def get_deal_records(self, params: DealRecordQueryParams) -> Dict:
        try:
            query = Q()
            
            # 添加城市筛选条件
            if params.city:
                query &= Q(community__city=params.city)
            
            # 基本筛选条件
            if params.search_keyword:
                query &= (
                    Q(community__name__icontains=params.search_keyword) |
                    Q(layout__icontains=params.search_keyword)
                )
            
            # 户型筛选
            if params.layout:
                if params.layout == 'other':
                    query &= ~Q(layout__startswith='1室') & \
                            ~Q(layout__startswith='2室') & \
                            ~Q(layout__startswith='3室') & \
                            ~Q(layout__startswith='4室')
                else:
                    query &= Q(layout__startswith=f'{params.layout}室')

            # 楼层筛选
            if params.floor_info:
                if params.floor_info == 'low':
                    query &= Q(floor_info__icontains='低')
                elif params.floor_info == 'middle':
                    query &= Q(floor_info__icontains='中')
                elif params.floor_info == 'high':
                    query &= Q(floor_info__icontains='高')

            # 获取基础查询
            base_query = self.model.all().prefetch_related('community')
            if query:
                base_query = base_query.filter(query)

            # 获取总数
            total = await base_query.count()

            # 排序和分页
            sort_field = f"{'-' if params.sort_direction == 'desc' else ''}{params.sort_by}"
            records = await base_query.order_by(sort_field)\
                .offset((params.page - 1) * params.page_size)\
                .limit(params.page_size)

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

    async def create_deal_record(self, data: DealRecordCreate) -> Dict:
        try:
            # 创建记录
            record = await self.create(data.model_dump(exclude_unset=True))
            
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

    async def update_deal_record(self, id: int, data: DealRecordUpdate) -> Dict:
        try:
            record = await self.update(id, data.model_dump(exclude_unset=True))
            
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
            print(f"Error in update_deal_record: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_deal_record(self, id: int) -> Dict:
        try:
            await self.remove(id)
            return {
                "code": 200,
                "msg": "删除成功",
                "data": None
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail="Record not found")

deal_record_controller = DealRecordController()

class OpportunityController(CRUDBase[Opportunity, OpportunityCreate, OpportunityUpdate]):
    def __init__(self):
        super().__init__(model=Opportunity)

    async def get_opportunity(self, id: int) -> Dict:
        try:
            opportunity = await self.get(id)
            return {
                "code": 200,
                "data": await opportunity.to_dict(),
                "message": "获取商机详情成功"
            }
        except Exception:
            return {
                "code": 404,
                "message": "商机不存在"
            }

    async def get_opportunities(self, params: OpportunityQueryParams) -> Dict:
        query = Q()
        
        if params.city:
            query &= Q(community__city=params.city.lower())
        if params.community_name:
            query &= Q(community_name__icontains=params.community_name)
        if params.status and params.status != 'all':
            query &= Q(status=params.status)

        total, items = await self.list(
            page=params.page,
            page_size=params.page_size,
            search=query
        )

        return {
            "code": 200,
            "data": {
                "total": total,
                "items": [await item.to_dict() for item in items]
            },
            "message": "获取商机列表成功"
        }

    async def create_opportunity(self, data: OpportunityCreate) -> Dict:
        try:
            opportunity = await self.create(data.dict())
            return {
                "code": 200,
                "data": await opportunity.to_dict(),
                "message": "创建商机成功"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_opportunity(self, id: int, data: OpportunityUpdate) -> Dict:
        try:
            opportunity = await self.update(id, data.dict(exclude_unset=True))
            return {
                "code": 200,
                "data": await opportunity.to_dict(),
                "message": "更新商机成功"
            }
        except Exception:
            return {"code": 404, "message": "商机不存在"}

    async def delete_opportunity(self, id: int) -> Dict:
        try:
            await self.remove(id)
            return {
                "code": 200,
                "message": "删除商机成功"
            }
        except Exception:
            return {"code": 404, "message": "商机不存在"}

opportunity_controller = OpportunityController() 