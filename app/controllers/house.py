from typing import List, Dict, Tuple
from fastapi import HTTPException, UploadFile
from tortoise.expressions import Q
from tortoise.functions import Count, Max
from app.models import User
from app.models.house import Community, Ershoufang, DealRecord, Opportunity, OpportunityFollowUp, Project, ConstructionPhase, PhaseMaterial
from app.schemas.house import (
    CommunityCreate, CommunityUpdate, CommunityResponse,
    ErshoufangCreate, ErshoufangUpdate, ErshoufangResponse,
    CommunityQueryParams, ErshoufangQueryParams,
    DealRecordCreate, DealRecordUpdate, DealRecordResponse,
    DealRecordQueryParams,
    OpportunityCreate, OpportunityUpdate, OpportunityQueryParams,
    OpportunityFollowUpCreate,
    ProjectCreate, ProjectUpdate,
    ConstructionPhaseCreate, ConstructionPhaseUpdate,
    PhaseMaterialCreate,
    ProjectQueryParams
)
from datetime import datetime
from app.core.crud import CRUDBase
import pandas as pd
from io import BytesIO
from tortoise.expressions import RawSQL
import re
import logging
from dateutil import parser

class CommunityController(CRUDBase[Community, CommunityCreate, CommunityUpdate]):
    def __init__(self):
        super().__init__(model=Community)
    
    async def get_communities(self, params: CommunityQueryParams) -> Dict:
        try:
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
        except Exception as e:
            logging.error(f"获取小区列表失败: {str(e)}")
            return {
                "code": 500,
                "msg": f"获取小区列表失败: {str(e)}",
                "data": None
            }

    async def check_duplicate(self, name: str, region: str, area: str, city: str) -> Community:
        """检查小区是否存在，如果存在返回小区对象，否则返回None"""
        try:
            return await self.model.filter(
                name=name,
                region=region,
                area=area,
                city=city.lower()
            ).first()
        except Exception as e:
            logging.error(f"检查小区重复失败: {str(e)}")
            return None

    async def create(self, data: CommunityCreate) -> Dict:
        """创建小区前检查是否重复"""
        try:
            # 检查是否存在重复小区
            existing = await self.check_duplicate(
                name=data.name,
                region=data.region,
                area=data.area,
                city=data.city
            )
            
            if existing:
                return {
                    "code": 400,
                    "msg": f"小区已存在：{data.region} {data.area} {data.name}",
                    "data": await CommunityResponse.from_tortoise_orm(existing)
                }
            
            community = await self.model.create(**data.dict())
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await CommunityResponse.from_tortoise_orm(community)
            }
        except Exception as e:
            logging.error(f"创建小区失败: {str(e)}")
            return {
                "code": 500,
                "msg": f"创建小区失败: {str(e)}",
                "data": None
            }

    async def update_community(self, id: int, data: CommunityUpdate) -> Dict:
        try:
            community = await self.update(id, data)
            if not community:
                return {
                    "code": 404,
                    "msg": "小区不存在",
                    "data": None
                }
            return {
                "code": 200,
                "msg": "更新成功",
                "data": await CommunityResponse.from_tortoise_orm(community)
            }
        except Exception as e:
            logging.error(f"更新小区失败: {str(e)}")
            return {
                "code": 500,
                "msg": f"更新小区失败: {str(e)}",
                "data": None
            }

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
                        except (TypeError, ValueError, IndexError):
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
        query = Q()
        if params.community_id:
            query &= Q(community_id=params.community_id)
        if params.city:
            query &= Q(city=params.city.lower())
        
        # 关键词搜索
        if params.search_keyword:
            query &= (
                Q(community_name__icontains=params.search_keyword) |
                Q(community__name__icontains=params.search_keyword) |
                Q(region__icontains=params.search_keyword) |
                Q(area__icontains=params.search_keyword)
            )
        
        # 户型筛选
        if params.layout:
            if params.layout == '其他':
                # 排除1-4室的情况
                exclude_patterns = ['1室', '一室', '2室', '二室', '3室', '三室', '4室', '四室']
                layout_query = Q()
                for pattern in exclude_patterns:
                    layout_query |= Q(layout__istartswith=pattern)
                query &= ~layout_query  # 使用 ~ 操作符取反
            else:
                layout_mapping = {
                    '一房': ['1室', '一室'],
                    '二房': ['2室', '二室'],
                    '三房': ['3室', '三室'],
                    '四房': ['4室', '四室']
                }
                if params.layout in layout_mapping:
                    layout_patterns = layout_mapping[params.layout]
                    layout_query = Q()
                    for pattern in layout_patterns:
                        layout_query |= Q(layout__istartswith=pattern)
                    query &= layout_query
        
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
        
        # 构建基础查询，包含所有记录
        base_query = self.model.filter(query).prefetch_related('community')
        
        # 计算总数
        total = await base_query.count()
        
        # 验证排序字段是否有效
        valid_sort_fields = ['listing_date', 'total_price', 'unit_price', 'size', 'created_at']
        sort_by = params.sort_by if params.sort_by in valid_sort_fields else 'listing_date'
        sort_direction = params.sort_direction if params.sort_direction in ['asc', 'desc'] else 'desc'
        
        # 获取分页数据
        items = await base_query\
            .order_by(f"{'-' if sort_direction == 'desc' else ''}{sort_by}")\
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
                
                # 确保返回 listing_date
                if item.listing_date:
                    item_dict['listing_date'] = item.listing_date.isoformat()
                
                # 计算楼层信息的逻辑修改
                if item.floor_number and item.total_floors:
                    # 优先使用楼层号计算
                    item_dict['floor_info'] = self.calculate_floor_info(
                        item.floor_number, 
                        item.total_floors
                    )
                elif item.floor:
                    # 如果没有具体楼层号，但有楼层描述，直接使用
                    floor_match = re.search(r'(低|中|高)楼层', item.floor)
                    if floor_match:
                        item_dict['floor_info'] = item.floor
                    else:
                        # 尝试从描述中提取信息
                        if '低' in item.floor:
                            item_dict['floor_info'] = '低楼层'
                        elif '中' in item.floor:
                            item_dict['floor_info'] = '中楼层'
                        elif '高' in item.floor:
                            item_dict['floor_info'] = '高楼层'
                
                result_items.append(item_dict)
            except Exception as e:
                continue
        
        return {
            "code": 200,
            "msg": "OK",
            "data": {
                "items": result_items,
                "total": total,
                "page": params.page,
                "page_size": params.page_size
            }
        }

    async def _get_filter_options(self) -> Dict:
        """获取筛选选项"""
        try:
            return {
                "regions": await self.model.all().distinct().values_list('region', flat=True),
                "areas": await self.model.all().distinct().values_list('area', flat=True),
                "layouts": await self.model.all().distinct().values_list('layout', flat=True),
                "orientations": await self.model.all().distinct().values_list('orientation', flat=True),
                "cities": await self.model.all().distinct().values_list('city', flat=True)
            }
        except Exception as e:
            logging.error(f"获取筛选选项失败: {str(e)}")
            return {
                "regions": [],
                "areas": [],
                "layouts": [],
                "orientations": [],
                "cities": []
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
            
            # 如果没有挂牌时间，才设置为当前日期
            if not create_data.get('listing_date'):
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
        
        # 处理楼层信息
        floor_number = update_data.get('floor_number')
        total_floors = update_data.get('total_floors')
        
        # 如果提供了任一楼层信息，重新计算楼层描述
        if floor_number is not None or total_floors is not None:
            # 获取当前值或使用更新值
            current_floor_number = floor_number if floor_number is not None else ershoufang.floor_number
            current_total_floors = total_floors if total_floors is not None else ershoufang.total_floors
            
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
                    
                    if floor_info:
                        update_data['floor'] = floor_info
                except (TypeError, ValueError) as e:
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
        
        # 更新数据
        await ershoufang.update_from_dict(update_data)
        await ershoufang.save()
        
        # 更新后重新获取数据
        ershoufang = await Ershoufang.get(id=id)
        
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
        try:
            ershoufang = await Ershoufang.get_or_none(id=id)
            if not ershoufang:
                return {
                    "code": 404,
                    "msg": "房源不存在",
                    "data": None
                }
            await ershoufang.delete()
            return {
                "code": 200,
                "msg": "删除成功",
                "data": None
            }
        except Exception as e:
            logging.error(f"删除房源失败: {str(e)}")
            return {
                "code": 500,
                "msg": f"删除房源失败: {str(e)}",
                "data": None
            }

    async def import_ershoufangs(self, file: UploadFile, city: str) -> Dict:
        # print(f"[Controller] 开始处理导入: filename={file.filename}, city={city}")
        
        try:
            # 读取Excel文件
            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.file)
            else:
                df = pd.read_csv(file.file)
            # print(f"[Controller] 成功读取文件, 数据行数: {len(df)}")
            # print(f"[Controller] 列名: {df.columns.tolist()}")
            
            success_count = 0
            updated_count = 0
            error_count = 0
            error_details = []
            
            def parse_chinese_date(date_str):
                """解析中文日期格式"""
                if pd.isna(date_str):
                    return None
                try:
                    # 处理 "YYYY年MM月DD日" 格式
                    if isinstance(date_str, str) and '年' in date_str:
                        date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                        return datetime.strptime(date_str, '%Y-%m-%d').date()
                    return pd.to_datetime(date_str).date()
                except Exception as e:
                    # print(f"日期解析失败: {date_str}, 错误: {str(e)}")
                    return None
            
            for index, row in df.iterrows():
                try:
                    # print(f"\n[Controller] 处理第{index+1}行数据:")
                    
                    # 转换Excel数据到数据库字段
                    house_data = {
                        'community_name': row['小区名称*'],
                        'house_id': str(row['平台房源ID']) if pd.notna(row['平台房源ID']) else None,
                        'region': row['所在区域'],
                        'area': row['所在商圈'],
                        'layout': row['户型*'],
                        'size': row['建筑面积*'],
                        'floor': row['楼层信息'] if pd.notna(row['楼层信息']) else None,
                        'floor_number': row.get('所在楼层'),
                        'total_floors': row.get('总楼层'),
                        'orientation': row['房屋朝向'] if pd.notna(row['房屋朝向']) else None,
                        'ladder_ratio': row['梯户比'] if pd.notna(row['梯户比']) else None,
                        'total_price': row['总价(万)*'],
                        'unit_price': row['单价(元/平)'] if pd.notna(row['单价(元/平)']) else None,
                        'listing_date': parse_chinese_date(row['挂牌时间']),
                        'last_transaction_date': parse_chinese_date(row['上次交易时间']),
                        'mortgage_info': row['抵押信息'] if pd.notna(row['抵押信息']) else None,
                        'layout_image': row['户型图链接'] if pd.notna(row['户型图链接']) else '',  # 将nan转换为空字符串
                        'house_link': row['房源链接'] if pd.notna(row['房源链接']) else '',  # 将nan转换为空字符串
                        'building_year': row.get('建筑年代'),
                        'building_structure': row.get('建筑结构'),
                        'platform_listing_id': str(row['平台房源ID']) if pd.notna(row['平台房源ID']) else None,
                        'data_source': 'import',  # 默认设置为'import'
                        'city': city.lower()
                    }
                    
                    # 处理楼层信息
                    floor_info = row['楼层信息']
                    if pd.notna(floor_info):
                        # 从"低楼层/共8层"这样的格式中提取总楼层
                        floor_parts = floor_info.split('/')
                        if len(floor_parts) == 2:
                            # 提取总楼层数
                            total_floors_str = floor_parts[1]  # 如"共8层"
                            total_floors = int(''.join(filter(str.isdigit, total_floors_str)))
                            house_data['total_floors'] = total_floors
                            
                            # 从第一部分提取楼层数字或描述
                            floor_description = floor_parts[0].strip()  # 如"低楼层"
                            
                            # 如果是具体楼层数
                            if '层' in floor_description and any(c.isdigit() for c in floor_description):
                                floor_number = int(''.join(filter(str.isdigit, floor_description)))
                                house_data['floor_number'] = floor_number
                            # 如果是描述性文字
                            else:
                                if '低' in floor_description:
                                    house_data['floor_number'] = max(1, int(total_floors * 0.2))
                                elif '中' in floor_description:
                                    house_data['floor_number'] = int(total_floors * 0.5)
                                elif '高' in floor_description:
                                    house_data['floor_number'] = int(total_floors * 0.8)
                                else:
                                    house_data['floor_number'] = 1
                            
                            # 使用计算出的楼层数重新生成楼层描述
                            floor_desc = self.calculate_floor_info(
                                house_data['floor_number'],
                                house_data['total_floors']
                            )
                            if floor_desc:
                                house_data['floor'] = floor_desc
                                house_data['floor_info'] = floor_desc
                    
                    # 如果没有楼层信息，设置默认值
                    if 'floor_number' not in house_data:
                        house_data['floor_number'] = 1
                    if 'total_floors' not in house_data:
                        house_data['total_floors'] = 1
                    if 'floor' not in house_data or 'floor_info' not in house_data:
                        floor_desc = self.calculate_floor_info(
                            house_data['floor_number'],
                            house_data['total_floors']
                        )
                        if floor_desc:
                            house_data['floor'] = floor_desc
                            house_data['floor_info'] = floor_desc
                    
                    # 确保非空字段有值
                    for key, value in house_data.items():
                        if value is None or (isinstance(value, str) and not value.strip()):
                            if key in ['community_name', 'layout', 'size', 'total_price']:
                                raise ValueError(f"必填字段 {key} 不能为空")
                    
                    # print(f"处理后的数据: {house_data}")
                    
                    # 检查小区是否存在，不存在则创建
                    community = await Community.filter(
                        name=house_data['community_name'],
                        city=house_data['city']
                    ).first()
                    
                    if not community:
                        # print(f"创建新小区: {house_data['community_name']}")
                        community = await Community.create(
                            name=house_data['community_name'],
                            city=house_data['city'],
                            region=house_data['region'],
                            area=house_data['area']
                        )
                    
                    # 添加小区ID到房源数据
                    house_data['community_id'] = community.id
                    
                    # 检查是否存在相同platform_listing_id的记录
                    existing_house = None
                    if house_data.get('platform_listing_id'):
                        existing_house = await Ershoufang.filter(platform_listing_id=house_data['platform_listing_id']).first()
                    
                    if existing_house:
                        # 更新已存在的记录
                        await Ershoufang.filter(id=existing_house.id).update(**house_data)
                        updated_count += 1
                        # print(f"第{index+1}行更新成功")
                    else:
                        # 创建新记录
                        await self.create_ershoufang(ErshoufangCreate(**house_data))
                        success_count += 1
                        # print(f"第{index+1}行创建成功")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"第{index+1}行创建房源失败: {str(e)}"
                    # print(f"[Controller] {error_msg}")
                    error_details.append(error_msg)
            
            result = {
                "code": 200,
                "msg": f"导入完成. 成功: {success_count}, 更新: {updated_count}, 失败: {error_count}",
                "data": {
                    "success_count": success_count,
                    "updated_count": updated_count,
                    "error_count": error_count,
                    "error_details": error_details
                }
            }
            # print(f"[Controller] 导入完成: {result}")
            return result
            
        except Exception as e:
            error_msg = f"导入过程异常: {str(e)}"
            # print(f"[Controller] {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    # 在 ErshoufangController 类中更新模板列定义
    IMPORT_COLUMNS = {
        'community_name': '小区名称',
        'house_id': '房源编号',
        'region': '所在区域',
        'area': '所在商圈',
        'layout': '户型',
        'size': '建筑面积',
        'floor': '楼层信息',
        'floor_number': '所在楼层',
        'total_floors': '总楼层',
        'orientation': '房屋朝向',
        'ladder_ratio': '梯户比',
        'total_price': '总价(万)',
        'unit_price': '单价(元/平)',
        'listing_date': '挂牌时间',
        'last_transaction_date': '上次交易时间',
        'mortgage_info': '抵押信息',
        'layout_image': '户型图链接',
        'house_link': '房源链接',
        'building_year': '建筑年代',
        'building_structure': '建筑结构',
        'platform_listing_id': '平台房源ID',
        'data_source': '数据来源'
    }

    # 更新列名映射
    EXCEL_TO_DB_MAPPING = {
        '小区名称': 'community_name',
        '房源编号': 'house_id',
        '所在区域': 'region',
        '所在商圈': 'area',
        '户型': 'layout',
        '建筑面积': 'size',
        '楼层信息': 'floor',
        '所在楼层': 'floor_number',
        '总楼层': 'total_floors',
        '房屋朝向': 'orientation',
        '梯户比': 'ladder_ratio',
        '总价': 'total_price',
        '单价': 'unit_price',
        '挂牌时间': 'listing_date',
        '上次交易时间': 'last_transaction_date',
        '抵押信息': 'mortgage_info',
        '户型图链接': 'layout_image',
        '房源链接': 'house_link',
        '建筑年代': 'building_year',
        '建筑结构': 'building_structure',
        '平台房源ID': 'platform_listing_id',
        '数据来源': 'data_source'
    }

ershoufang_controller = ErshoufangController()

class DealRecordController(CRUDBase[DealRecord, DealRecordCreate, DealRecordUpdate]):
    def __init__(self):
        super().__init__(model=DealRecord)

    def _convert_timestamp_to_date(self, timestamp):
        """将时间戳转换为日期对象"""
        try:
            # 尝试处理毫秒级时间戳
            if len(str(timestamp)) > 10:
                timestamp = timestamp / 1000
            return datetime.fromtimestamp(timestamp).date()
        except (ValueError, OSError, TypeError) as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid timestamp format: {timestamp}"
            )

    async def list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Q = None,
        order: List[str] = None,
    ) -> Tuple[int, List[DealRecord]]:
        """
        获取列表数据，对于相同的 source_transaction_id 只返回最新更新的记录
        """
        try:
            base_query = search if search else Q()
            
            # 获取每个 source_transaction_id 的最新记录的 id
            latest_ids = await DealRecord.filter(base_query)\
                .group_by('source_transaction_id')\
                .annotate(latest_id=Max('id'))\
                .values_list('latest_id', flat=True)
                
            # 构建最终查询，确保应用基础查询条件
            query = DealRecord.filter(
                (Q(id__in=latest_ids) | Q(source_transaction_id__isnull=True)) & base_query
            )
            
            # 计算总数
            total = await query.count()
            
            # 应用排序和分页
            if order:
                for o in order:
                    if o.startswith('-'):
                        query = query.order_by(o)
                    else:
                        query = query.order_by(o)
                        
            items = await query.offset((page - 1) * page_size).limit(page_size)
            
            return total, items
        except Exception as e:
            logging.error(f"获取成交记录列表失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取成交记录列表失败: {str(e)}")

    async def get_deal_records(self, params: DealRecordQueryParams) -> Dict:
        """获取成交记录列表"""
        try:
            logging.info(f"接收到查询参数: {params}")
            query = Q()
            
            if params.community_id:
                query &= Q(community_id=params.community_id)
                logging.info(f"添加小区ID筛选条件: {params.community_id}")
                
            if params.city:
                city = params.city.lower()
                query &= Q(city=city)
                logging.info(f"添加城市筛选条件: {city}")
                
            if params.search_keyword:
                logging.info(f"添加小区名称搜索条件: {params.search_keyword}")
                query &= Q(community_name__icontains=params.search_keyword)
                
            if params.layout:
                query &= Q(layout=params.layout)
                
            if params.floor_info:
                query &= Q(floor_info=params.floor_info)

            # 构建排序条件
            order = []
            if params.sort_by:
                order.append(f"{'-' if params.sort_direction == 'desc' else ''}{params.sort_by}")
                
            # 获取数据
            total, items = await self.list(
                page=params.page,
                page_size=params.page_size,
                search=query,
                order=order
            )
            
            response_items = []
            for item in items:
                try:
                    item_dict = {
                        'id': item.id,
                        'community_id': item.community_id,
                        'community_name': item.community_name,
                        'region': item.region,
                        'area': item.area,
                        'city': item.city,
                        'source': item.source,
                        'source_transaction_id': item.source_transaction_id,
                        'layout': item.layout,
                        'size': item.size,
                        'floor_info': item.floor_info,
                        'floor_number': item.floor_number,
                        'total_floors': item.total_floors,
                        'orientation': item.orientation,
                        'listing_price': item.listing_price,  # 挂牌价
                        'total_price': item.total_price,
                        'unit_price': item.unit_price,
                        'tags': item.tags,
                        'location': item.location,
                        'decoration': item.decoration,
                        'agency': item.agency,
                        'deal_date': item.deal_date.isoformat() if item.deal_date else None,
                        'deal_cycle': item.deal_cycle,
                        'house_link': item.house_link,  # 房源链接
                        'layout_image': item.layout_image,  # 户型图链接
                        'building_year': item.building_year,
                        'building_structure': item.building_structure,
                        'platform_house_id': item.source_transaction_id,  # 使用source_transaction_id作为platform_house_id
                        'entry_time': item.entry_time.isoformat() if item.entry_time else None,
                        'created_at': item.created_at.isoformat() if item.created_at else None,
                        'updated_at': item.updated_at.isoformat() if item.updated_at else None
                    }
                    response_items.append(item_dict)
                except Exception as e:
                    logging.error(f"处理成交记录数据失败: {str(e)}")
                    continue

            return {
                "code": 200,
                "msg": "OK",
                "data": {
                    "items": response_items,
                    "total": total,
                    "page": params.page,
                    "page_size": params.page_size
                }
            }
        except Exception as e:
            logging.error(f"获取成交记录列表失败: {str(e)}")
            return {
                "code": 500,
                "msg": f"获取成交记录列表失败: {str(e)}",
                "data": None
            }

    async def create_deal_record(self, data: DealRecordCreate) -> Dict:
        try:
            # 获取小区信息
            community = await Community.get_or_none(id=data.community_id)
            if not community:
                raise HTTPException(status_code=404, detail="Community not found")
            
            # 添加区域和商圈信息
            create_data = data.dict()
            create_data.update({
                'community_name': community.name,
                'region': community.region,  # 从小区获取区域
                'area': community.area,      # 从小区获取商圈
                'city': community.city
            })
            
            deal_record = await self.create(create_data)
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await deal_record.to_dict()
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_deal_record(self, id: int, data: DealRecordUpdate) -> Dict:
        try:
            deal_record = await DealRecord.get_or_none(id=id)
            if not deal_record:
                raise HTTPException(status_code=404, detail="Deal record not found")
            
            # 准备更新数据
            update_data = data.model_dump(exclude_unset=True)
            
            # 处理日期字段
            deal_date = update_data.get('deal_date')
            if deal_date:
                if isinstance(deal_date, (int, float)):
                    # 处理时间戳
                    update_data['deal_date'] = self._convert_timestamp_to_date(deal_date)
                elif isinstance(deal_date, str):
                    try:
                        update_data['deal_date'] = datetime.strptime(deal_date, '%Y-%m-%d').date()
                    except ValueError:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Invalid date format. Expected YYYY-MM-DD"
                        )
            
            # 如果小区 ID 变更，更新相关信息
            if 'community_id' in update_data:
                community = await Community.get_or_none(id=update_data['community_id'])
                if not community:
                    raise HTTPException(status_code=404, detail="Community not found")
                update_data.update({
                    'community_name': community.name,
                    'region': community.region,
                    'area': community.area,
                    'city': community.city
                })
            
            # 更新数据
            await deal_record.update_from_dict(update_data)
            await deal_record.save()
            
            # 格式化返回数据
            response_data = await deal_record.to_dict()
            
            return {
                "code": 200,
                "msg": "更新成功",
                "data": response_data
            }
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

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

    async def import_deal_records(self, file: UploadFile, city: str) -> Dict:
        try:
            contents = await file.read()
            # 根据文件扩展名选择不同的读取方式
            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(contents))
            else:
                df = pd.read_csv(BytesIO(contents))
            df.columns = df.columns.str.replace('*', '').str.strip()
            
            # 验证必要的列
            required_columns = ['小区名称', '建筑面积', '成交价', '成交时间']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"缺少必要的列: {', '.join(missing_columns)}"
                )
            
            success_count = 0
            error_list = []
            
            for _, row in df.iterrows():
                try:
                    # 检查必填字段
                    if pd.isna(row['小区名称']) or pd.isna(row['建筑面积']) or \
                       pd.isna(row['成交价']) or pd.isna(row['成交时间']):
                        error_list.append({
                            "name": row.get('小区名称', '未知'),
                            "error": "必填字段不能为空"
                        })
                        continue
                    
                    # 查找或创建小区
                    community = await Community.filter(
                        name=row['小区名称'],
                        city=city.lower()
                    ).first()
                    
                    if not community:
                        # 创建新小区
                        community = await Community.create(
                            name=row['小区名称'],
                            city=city.lower(),
                            region=row.get('所在区域', ''),
                            area=row.get('所在商圈', ''),
                            building_year=row.get('建筑年代'),
                            building_type=row.get('建筑结构')
                        )
                    
                    # 准备数据
                    deal_record_data = {
                        "community_id": community.id,
                        "community_name": row['小区名称'],
                        "region": row.get('所在区域', community.region),
                        "area": row.get('所在商圈', community.area),
                        "city": city.lower(),
                        "source": row.get('数据来源', 'import'),
                        "source_transaction_id": row.get('平台房源ID'),
                        "size": float(row['建筑面积']),
                        "total_price": float(row['成交价']),
                        "deal_date": pd.to_datetime(row['成交时间']).date()
                    }
                    
                    # 处理其他可选字段
                    optional_fields = {
                        '户型': 'layout',
                        '楼层信息': 'floor_info',
                        '所在楼层': 'floor_number',
                        '总楼层': 'total_floors',
                        '房屋朝向': 'orientation',
                        '挂牌价': 'listing_price',
                        '单价': 'unit_price',
                        '成交周期': 'deal_cycle',
                        '标签': 'tags',
                        '户型图链接': 'layout_image',
                        '房源链接': 'house_link',
                        '建筑年代': 'building_year',
                        '建筑结构': 'building_structure',
                        '位置': 'location',
                        '装修': 'decoration',
                        '中介公司': 'agency'
                    }
                    
                    for excel_col, db_col in optional_fields.items():
                        if excel_col in row and not pd.isna(row[excel_col]):
                            value = row[excel_col]
                            # 特殊字段处理
                            if db_col in ['floor_number', 'total_floors', 'deal_cycle', 'building_year']:
                                try:
                                    value = int(float(value))
                                except (ValueError, TypeError):
                                    continue
                            elif db_col in ['listing_price', 'unit_price']:
                                try:
                                    value = float(value)
                                except (ValueError, TypeError):
                                    continue
                            deal_record_data[db_col] = value
                    
                    # 如果没有单价，则计算单价
                    if 'unit_price' not in deal_record_data:
                        deal_record_data['unit_price'] = \
                            deal_record_data['total_price'] * 10000 / deal_record_data['size']
                    
                    # 创建成交记录
                    await self.model.create(**deal_record_data)
                    success_count += 1
                    
                except Exception as e:
                    error_list.append({
                        "name": row.get('小区名称', '未知'),
                        "error": str(e)
                    })
            
            return {
                "code": 200,
                "msg": "导入成功",
                "data": {
                    "success_count": success_count,
                    "error_count": len(error_list),
                    "errors": error_list
                }
            }
            
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # 添加导入模板列定义
    IMPORT_COLUMNS = {
        'community_name': '小区名称',
        'region': '所在区域',
        'area': '所在商圈',
        'layout': '户型',
        'size': '建筑面积',
        'floor_info': '楼层信息',
        'floor_number': '所在楼层',
        'total_floors': '总楼层',
        'orientation': '房屋朝向',
        'listing_price': '挂牌价',
        'total_price': '成交价',
        'unit_price': '单价',
        'deal_date': '成交时间',
        'deal_cycle': '成交周期',
        'tags': '标签',
        'layout_image': '户型图链接',
        'house_link': '房源链接',
        'city': '所在城市',
        'building_year': '建筑年代',
        'building_structure': '建筑结构',
        'location': '位置',
        'decoration': '装修',
        'agency': '中介公司',
        'source': '数据来源',
        'source_transaction_id': '平台房源ID'
    }

deal_record_controller = DealRecordController()

class OpportunityController(CRUDBase[Opportunity, OpportunityCreate, OpportunityUpdate]):
    def __init__(self):
        super().__init__(model=Opportunity)

    async def get_opportunity(self, id: int) -> Dict:
        try:
            opportunity = await Opportunity.get_or_none(id=id)
            if not opportunity:
                raise HTTPException(status_code=404, detail="商机不存在")
            return {
                "code": 200,
                "data": await opportunity.to_dict(),
                "message": "获取商机详情成功"
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_opportunities(self, params: OpportunityQueryParams) -> Dict:
        """获取商机列表"""
        try:
            query = Q()
            
            # 通过关联的小区来过滤城市
            if params.city:
                query &= Q(community__city=params.city.lower())
                
            if params.community_name:
                query &= Q(community_name__icontains=params.community_name)
                
            if params.status:
                if isinstance(params.status, list):
                    query &= Q(status__in=params.status)
                else:
                    query &= Q(status=params.status)

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
                    "items": [await item.to_dict() for item in items],
                    "total": total,
                    "page": params.page,
                    "page_size": params.page_size
                }
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def create_opportunity(self, data: OpportunityCreate) -> Dict:
        try:
            opportunity = await Opportunity.create(**data.dict())
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await opportunity.to_dict()
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_opportunity(self, id: int, data: OpportunityUpdate) -> Dict:
        try:
            opportunity = await Opportunity.get_or_none(id=id)
            if not opportunity:
                raise HTTPException(status_code=404, detail="商机不存在")
                
            await opportunity.update_from_dict(data.dict(exclude_unset=True))
            await opportunity.save()
            return {
                "code": 200,
                "msg": "更新商机成功",
                "data": await opportunity.to_dict()
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_opportunity(self, id: int) -> Dict:
        try:
            opportunity = await Opportunity.get_or_none(id=id)
            if not opportunity:
                raise HTTPException(status_code=404, detail="商机不存在")
                
            await opportunity.delete()
            return {
                "code": 200,
                "message": "删除商机成功"
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

opportunity_controller = OpportunityController()

class OpportunityFollowUpController(CRUDBase[OpportunityFollowUp, OpportunityFollowUpCreate, None]):
    async def create_follow_up(self, obj_in: OpportunityFollowUpCreate, user_id: int) -> dict:
        """创建跟进记录"""
        try:
            # 获取商机
            opportunity = await Opportunity.get_or_none(id=obj_in.opportunity_id)
            if not opportunity:
                raise HTTPException(status_code=404, detail="商机不存在")
                
            # 创建跟进记录
            follow_up_dict = obj_in.model_dump()
            follow_up_dict['user_id'] = user_id
            follow_up = await self.model.create(**follow_up_dict)
            
            # 根据跟进结果更新商机状态
            if obj_in.follow_up_result == '已签约':
                opportunity.status = '已签约'
            elif obj_in.follow_up_result == '已放弃':
                opportunity.status = '已放弃'
            elif obj_in.follow_up_result == '已评估':
                opportunity.status = '已评估'
                
            await opportunity.save()
            
            # 构造返回数据
            user = await User.get_or_none(id=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
                
            return {
                'code': 200,
                'msg': '创建成功',
                'data': {
                    'id': follow_up.id,
                    'opportunity_id': follow_up.opportunity_id,
                    'follow_up_time': follow_up.follow_up_time,
                    'follow_up_method': follow_up.follow_up_method,
                    'follow_up_content': follow_up.follow_up_content,
                    'authorized_price': follow_up.authorized_price,
                    'price_adjusted': follow_up.price_adjusted,
                    'adjust_reason': follow_up.adjust_reason,
                    'follow_up_result': follow_up.follow_up_result,
                    'user_id': user.id,
                    'user_name': user.username,
                    'created_at': follow_up.created_at,
                    'updated_at': follow_up.updated_at
                }
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_follow_ups(self, opportunity_id: int) -> dict:
        """获取商机的所有跟进记录"""
        try:
            # 检查商机是否存在
            opportunity = await Opportunity.get_or_none(id=opportunity_id)
            if not opportunity:
                raise HTTPException(status_code=404, detail="商机不存在")
                
            follow_ups = await self.model.filter(
                opportunity_id=opportunity_id
            ).order_by('-follow_up_time').prefetch_related('user')
            
            data = []
            for follow_up in follow_ups:
                data.append({
                    'id': follow_up.id,
                    'opportunity_id': follow_up.opportunity_id,
                    'follow_up_time': follow_up.follow_up_time,
                    'follow_up_method': follow_up.follow_up_method,
                    'follow_up_content': follow_up.follow_up_content,
                    'authorized_price': follow_up.authorized_price,
                    'price_adjusted': follow_up.price_adjusted,
                    'adjust_reason': follow_up.adjust_reason,
                    'follow_up_result': follow_up.follow_up_result,
                    'user_id': follow_up.user.id,
                    'user_name': follow_up.user.username,
                    'created_at': follow_up.created_at,
                    'updated_at': follow_up.updated_at
                })
                
            return {
                'code': 200,
                'msg': '获取成功',
                'data': data
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

opportunity_follow_up_controller = OpportunityFollowUpController(OpportunityFollowUp)

class ProjectController(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def __init__(self):
        super().__init__(model=Project)
    
    async def create_project(self, data: dict):
        """创建项目"""
        try:
            # 确保有商机信息
            opportunity = await Opportunity.get_or_none(id=data.get('opportunity_id'))
            if not opportunity:
                raise ValueError("商机不存在")
            
            # 创建项目
            try:
                # 使用 model.create() 而不是 Project.create()
                project = await self.model.create(
                    opportunity_id=data['opportunity_id'],
                    community_name=str(data['community_name']).strip(),  # 确保是非空字符串
                    address=data['address'],
                    contract_price=data['contract_price'],
                    contract_period=data['contract_period'],
                    signer=data['signer'],
                    delivery_date=data['delivery_date'],
                    current_phase=data['current_phase'],
                    decoration_company=data.get('decoration_company')  # 传递装修公司字段
                )
                return {
                    "code": 200,
                    "message": "创建成功",
                    "data": await project.to_dict()
                }
            except Exception as create_error:
                raise create_error
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_project_details(self, project_id: int):
        """获取项目详情"""
        try:
            project = await self.model.get_or_none(id=project_id).prefetch_related(
                'phases',  # 修改为正确的关联名称
                'opportunity'
            )
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
            
            return {
                "code": 200,
                "msg": "获取成功",
                "data": await project.to_dict()
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_projects(self, params: ProjectQueryParams) -> Dict:
        try:
            # 构建基础查询
            query = Q()
            
            # 添加筛选条件
            if params.city:
                # 通过商机关联的小区筛选城市
                query &= Q(opportunity__community__city=params.city.lower())

            if params.opportunity_id:
                query &= Q(opportunity_id=params.opportunity_id)
            if params.current_phase:
                query &= Q(current_phase=params.current_phase)
            if params.signer:
                query &= Q(signer__icontains=params.signer)
            if params.delivery_date_start:
                query &= Q(delivery_date__gte=params.delivery_date_start)
            if params.delivery_date_end:
                query &= Q(delivery_date__lte=params.delivery_date_end)

            # 构建查询，预加载关联数据
            base_query = self.model.filter(query)\
                .prefetch_related('phases', 'opportunity', 'opportunity__community')
            
            # 计算总数
            total = await base_query.count()

            # 获取分页数据
            offset = (params.page - 1) * params.page_size
            items = await base_query.order_by('-created_at')\
                .offset(offset).limit(params.page_size)

            # 处理返回数据
            result_items = []
            for item in items:
                try:
                    item_dict = await item.to_dict()
                    # 添加商机关联的小区城市信息
                    if hasattr(item, 'opportunity') and item.opportunity:
                        if hasattr(item.opportunity, 'community') and item.opportunity.community:
                            item_dict['city'] = item.opportunity.community.city
                        else:
                            item_dict['city'] = 'shanghai'  # 默认城市
                    else:
                        item_dict['city'] = 'shanghai'  # 默认城市
                    result_items.append(item_dict)
                except Exception as item_e:
                    logging.error(f"处理项目数据失败: {str(item_e)}")
                    continue

            return {
                "code": 200,
                "msg": "OK",
                "data": {
                    "items": result_items,
                    "total": total,
                    "page": params.page,
                    "page_size": params.page_size
                }
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update(self, id: int, data: ProjectUpdate) -> Dict:
        """更新项目"""
        try:
            # 获取项目时预加载关联的商机数据
            project = await self.model.get(id=id).prefetch_related('opportunity', 'phases')
            update_data = data.dict(exclude_unset=True)
            
            # 如果项目没有户型图，layout_image 可能是 QuerySet，需要特殊处理
            if hasattr(project, 'layout_image') and isinstance(project.layout_image, object) and not isinstance(project.layout_image, str):
                project.layout_image = None
            
            await project.update_from_dict(update_data)
            await project.save()
            
            return {
                "code": 200,
                "message": "更新成功",
                "data": await project.to_dict()
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_project(self, project_id: int) -> Dict:
        """删除项目"""
        try:
            project = await self.model.get(id=project_id)
            if not project:
                raise HTTPException(status_code=404, detail="项目不存在")
            
            # 删除项目相关的施工阶段和材料
            await ConstructionPhase.filter(project_id=project_id).delete()
            phases = await ConstructionPhase.filter(project_id=project_id).values_list('id', flat=True)
            if phases:
                await PhaseMaterial.filter(phase_id__in=phases).delete()
            
            # 删除项目本身
            await project.delete()
            
            return {
                "code": 200,
                "msg": "删除成功",
                "data": None
            }
        except Exception as e:
            logging.error(f"删除项目失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"删除项目失败: {str(e)}")

class ConstructionPhaseController(CRUDBase[ConstructionPhase, ConstructionPhaseCreate, ConstructionPhaseUpdate]):
    def __init__(self):
        super().__init__(model=ConstructionPhase)
    
    async def create_phase(self, data: ConstructionPhaseCreate) -> Dict:
        try:
            # 验证项目是否存在
            project = await Project.get_or_none(id=data.project_id)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # 创建施工阶段
            phase = await self.model.create(**data.dict())
            
            # 更新项目当前阶段
            project.current_phase = data.phase_type
            await project.save()
            
            return {
                "code": 200,
                "msg": "创建成功",
                "data": await phase.to_dict()
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

class PhaseMaterialController(CRUDBase[PhaseMaterial, PhaseMaterialCreate, None]):
    def __init__(self):
        super().__init__(model=PhaseMaterial)
    
    async def upload_material(self, data: PhaseMaterialCreate) -> Dict:
        try:
            # 验证施工阶段是否存在
            phase = await ConstructionPhase.get_or_none(id=data.phase_id)
            if not phase:
                raise HTTPException(status_code=404, detail="Construction phase not found")
            
            # 创建阶段材料记录
            material = await self.model.create(**data.dict())
            
            return {
                "code": 200,
                "msg": "上传成功",
                "data": await material.to_dict()
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def upload_phase_material(self, phase_id: int, file: UploadFile, material_type: str, uploader: str) -> Dict:
        try:
            # 验证施工阶段
            phase = await ConstructionPhase.get_or_none(id=phase_id)
            if not phase:
                raise HTTPException(status_code=404, detail="Construction phase not found")
            
            # 保存文件
            file_path = await self.save_file(file)
            
            # 创建材料记录
            material = await PhaseMaterial.create(
                phase_id=phase_id,
                material_type=material_type,
                file_path=file_path,
                uploader=uploader
            )
            
            return {
                "code": 200,
                "msg": "上传成功",
                "data": await material.to_dict()
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# 初始化控制器实例
project_controller = ProjectController()
construction_phase_controller = ConstructionPhaseController()
phase_material_controller = PhaseMaterialController() 