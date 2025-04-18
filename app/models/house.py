from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import NoValuesFetched
from app.models.base import BaseModel, TimestampMixin
from datetime import datetime, date
from tortoise.validators import MinValueValidator, MaxValueValidator

class Community(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200, null=False, description='小区名称')
    city = fields.CharField(max_length=50, null=False, default='shanghai', description='城市')
    region = fields.CharField(max_length=100, null=False, default='', description='区域')
    area = fields.CharField(max_length=100, null=False, default='', description='商圈')
    address = fields.CharField(max_length=500, null=True, description='地址')
    building_type = fields.CharField(max_length=100, null=True, description='建筑类型')
    property_rights = fields.CharField(max_length=200, null=True, description='交易权属')
    total_houses = fields.IntField(null=True, description='房屋总数', 
                                 validators=[MinValueValidator(0), MaxValueValidator(100000)])
    building_year = fields.IntField(null=True, description='建筑年代',
                                  validators=[MinValueValidator(1800), MaxValueValidator(2100)])
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = "community"
        table_description = "小区信息表"

    async def save(self, *args, **kwargs):
        # 确保保存时城市值是小写的
        if self.city:
            self.city = self.city.lower()
        await super().save(*args, **kwargs)

    @classmethod
    async def create(cls, **kwargs):
        # 确保创建时城市值是小写的
        if 'city' in kwargs:
            kwargs['city'] = kwargs['city'].lower()
        return await super().create(**kwargs)

class Ershoufang(Model):
    id = fields.IntField(pk=True)
    community = fields.ForeignKeyField('models.Community', related_name='houses')
    community_name = fields.CharField(max_length=200)
    house_id = fields.CharField(max_length=100, null=True)  # 房源ID
    region = fields.CharField(max_length=100, null=True)  # 区域
    area = fields.CharField(max_length=100, null=True)  # 商圈
    layout = fields.CharField(max_length=100)  # 户型
    size = fields.FloatField(validators=[MinValueValidator(1), MaxValueValidator(10000)], description='建筑面积(平方米)')
    floor = fields.CharField(max_length=100, null=True)  # 楼层描述
    floor_number = fields.IntField(null=True, validators=[MinValueValidator(-10), MaxValueValidator(150)])  # 所在楼层
    total_floors = fields.IntField(null=True, validators=[MinValueValidator(1), MaxValueValidator(150)])  # 总楼层
    orientation = fields.CharField(max_length=100, null=True)  # 朝向
    ladder_ratio = fields.CharField(max_length=100, null=True)  # 梯户比
    total_price = fields.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1000000000)], description='总价(万元)')
    unit_price = fields.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(1000000)], description='单价(元/平)')
    listing_date = fields.DateField(null=True)  # 挂牌时间
    last_transaction_date = fields.DateField(null=True)  # 上次交易时间
    mortgage_info = fields.CharField(max_length=500, null=True)  # 抵押信息
    layout_image = fields.CharField(max_length=1000, null=True)  # 户型图链接
    ke_code = fields.CharField(max_length=100, null=True)  # 贝壳编号
    house_link = fields.CharField(max_length=1000, null=True)  # 房源链接
    city = fields.CharField(max_length=50)  # 城市
    # 修改这两个字段的 null 参数为 True
    building_year = fields.IntField(
        null=True,  # 确保可以为空
        validators=[MinValueValidator(1800), MaxValueValidator(2100)],
        description='建筑年代'
    )
    building_structure = fields.CharField(
        max_length=100,
        null=True,  # 确保可以为空
        description='楼栋结构'
    )
    data_source = fields.CharField(max_length=50)  # 数据来源
    platform_listing_id = fields.CharField(max_length=100, null=True)  # 来源平台房源ID
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = "ershoufang"

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "community_id": self.community_id,
            "community_name": self.community_name,
            "region": self.region,
            "area": self.area,
            "city": self.city,
            "layout": self.layout,
            "floor_number": self.floor_number,
            "total_floors": self.total_floors,
            "floor": self.floor,
            "orientation": self.orientation,
            "size": self.size,
            "total_price": self.total_price,
            "unit_price": self.unit_price,
            "data_source": self.data_source,
            "ladder_ratio": self.ladder_ratio,
            "mortgage_info": self.mortgage_info,
            "layout_image": self.layout_image,
            "house_link": self.house_link,
            "house_id": self.house_id,
            "ke_code": self.ke_code,
            "listing_date": self.listing_date.isoformat() if self.listing_date else None,
            "last_transaction_date": self.last_transaction_date.isoformat() if self.last_transaction_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DealRecord(BaseModel, TimestampMixin):
    id = fields.IntField(pk=True)
    house_id = fields.CharField(max_length=100, null=True, description='房源ID')
    community = fields.ForeignKeyField('models.Community', related_name='deal_records')
    community_name = fields.CharField(max_length=200, null=False, description='小区名称')
    region = fields.CharField(max_length=100, null=False, description='所在区域')
    area = fields.CharField(max_length=100, null=False, description='所在商圈')
    layout = fields.CharField(max_length=100, null=True, description='户型')
    size = fields.FloatField(null=False, description='建筑面积',
                           validators=[MinValueValidator(1), MaxValueValidator(10000)])
    floor_info = fields.CharField(max_length=100, null=True, description='楼层信息')
    floor_number = fields.IntField(null=True, description='所在楼层',
                                 validators=[MinValueValidator(-10), MaxValueValidator(150)])
    total_floors = fields.IntField(null=True, description='总楼层',
                                 validators=[MinValueValidator(1), MaxValueValidator(150)])
    orientation = fields.CharField(max_length=100, null=True, description='房屋朝向')
    listing_price = fields.FloatField(null=True, description='挂牌价',
                                    validators=[MinValueValidator(0), MaxValueValidator(1000000000)])
    total_price = fields.FloatField(null=False, description='成交价',
                                  validators=[MinValueValidator(0), MaxValueValidator(1000000000)])
    unit_price = fields.FloatField(null=True, description='单价(元/平)',
                                 validators=[MinValueValidator(0), MaxValueValidator(1000000)])
    deal_date = fields.DateField(null=False, description='成交日期')
    deal_cycle = fields.IntField(null=True, description='成交周期',
                               validators=[MinValueValidator(0), MaxValueValidator(3650)])
    tags = fields.CharField(max_length=500, null=True, description='标签')
    layout_image = fields.CharField(max_length=1000, null=True, description='户型图链接')
    house_link = fields.CharField(max_length=1000, null=True, description='房源链接')
    city = fields.CharField(max_length=50, null=False, description='所在城市')
    building_year = fields.IntField(null=True, description='建筑年代',
                                  validators=[MinValueValidator(1800), MaxValueValidator(2100)])
    building_structure = fields.CharField(max_length=100, null=True, description='建筑结构')
    location = fields.CharField(max_length=500, null=True, description='位置')
    decoration = fields.CharField(max_length=100, null=True, description='装修')
    agency = fields.CharField(max_length=200, null=True, description='中介公司')
    source = fields.CharField(max_length=50, null=False, description='数据来源')
    source_transaction_id = fields.CharField(max_length=100, null=True, description='来源平台交易ID')
    entry_time = fields.DatetimeField(auto_now_add=True, description='数据入库时间')
    original_data = fields.JSONField(null=True, description='原始数据')

    # 标记为已废弃的字段
    data_source = fields.CharField(max_length=50, null=True, description='数据来源', deprecated=True)
    platform_listing_id = fields.CharField(max_length=100, null=True, description='平台房源ID', deprecated=True)

    class Meta:
        table = "deal_record"
        table_description = "成交记录表"

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        base_dict = await super().to_dict()
        base_dict.update({
            "source": self.source,
            "source_transaction_id": self.source_transaction_id,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "original_data": self.original_data,
            "deal_date": self.deal_date.isoformat() if self.deal_date else None
        })
        return base_dict

class Opportunity(Model):
    id = fields.IntField(pk=True)
    community = fields.ForeignKeyField('models.Community', related_name='opportunities')
    community_name = fields.CharField(max_length=200, null=True)
    layout = fields.CharField(max_length=100, null=True)
    floor = fields.CharField(max_length=100, null=True)
    area = fields.FloatField(null=True, validators=[MinValueValidator(1), MaxValueValidator(10000)])
    total_price = fields.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(1000000000)])
    unit_price = fields.FloatField(null=True, validators=[MinValueValidator(0), MaxValueValidator(1000000)])
    address = fields.CharField(max_length=500, null=True)
    building_number = fields.CharField(max_length=100, null=True)
    room_number = fields.CharField(max_length=100, null=True)
    is_full_five = fields.BooleanField(default=False)
    is_full_two = fields.BooleanField(default=False)
    is_unique = fields.BooleanField(default=False)
    transaction_source = fields.CharField(max_length=100, null=True)
    layout_image = fields.CharField(max_length=1000, null=True)
    interior_image = fields.CharField(max_length=1000, null=True)
    location_image = fields.CharField(max_length=1000, null=True)
    opportunity_owner = fields.CharField(max_length=200, null=True)
    belonging_owner = fields.CharField(max_length=200, null=True)
    status = fields.CharField(max_length=50, default='待评估')
    remarks = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    ershoufang = fields.ForeignKeyField('models.Ershoufang', null=True, related_name='opportunities')

    # 保留关联字段
    follow_ups: fields.ReverseRelation["OpportunityFollowUp"]

    class Meta:
        table = "opportunity"
        table_description = "商机信息表"

    async def to_dict(self) -> dict:
        return {
            "id": self.id,
            "community_id": self.community_id,
            "community_name": self.community_name,
            "layout": self.layout,
            "floor": self.floor,
            "area": self.area,
            "total_price": self.total_price,
            "unit_price": self.unit_price,
            "status": self.status,
            "layout_image": self.layout_image,
            "interior_image": self.interior_image or None,
            "location_image": self.location_image or None,
            "address": self.address,
            "building_number": self.building_number,
            "room_number": self.room_number,
            "is_full_five": self.is_full_five,
            "is_full_two": self.is_full_two,
            "is_unique": self.is_unique,
            "transaction_source": self.transaction_source,
            "opportunity_owner": self.opportunity_owner,
            "belonging_owner": self.belonging_owner,
            "remarks": self.remarks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class OpportunityFollowUp(Model):
    """商机跟进记录"""
    id = fields.IntField(pk=True, description='跟进记录ID')
    opportunity = fields.ForeignKeyField(
        'models.Opportunity', 
        related_name='follow_ups',
        description='关联的商机',
        on_delete=fields.CASCADE
    )
    follow_up_time = fields.DatetimeField(description='跟进时间')
    follow_up_method = fields.CharField(max_length=50, description='跟进方式')
    follow_up_content = fields.TextField(description='跟进内容')
    authorized_price = fields.FloatField(
        null=True,
        description='本次授权价格',
        validators=[MinValueValidator(0), MaxValueValidator(1000000000)]
    )
    price_adjusted = fields.BooleanField(default=False, description='价格是否调整')
    adjust_reason = fields.TextField(null=True, description='价格调整原因')
    follow_up_result = fields.CharField(max_length=50, description='跟进结果')
    user = fields.ForeignKeyField(
        'models.User',
        related_name='follow_ups',
        description='跟进人',
        on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = "opportunity_follow_up"
        table_description = "商机跟进记录表"
        ordering = ["-follow_up_time"]
        indexes = [
            "opportunity_id",
            "user_id",
            "follow_up_time"
        ]

    async def to_dict(self) -> dict:
        """转换为字典"""
        user = await self.user.first()
        return {
            'id': self.id,
            'opportunity_id': self.opportunity_id,
            'follow_up_time': self.follow_up_time,
            'follow_up_method': self.follow_up_method,
            'follow_up_content': self.follow_up_content,
            'authorized_price': self.authorized_price,
            'price_adjusted': self.price_adjusted,
            'adjust_reason': self.adjust_reason,
            'follow_up_result': self.follow_up_result,
            'user_id': self.user_id,
            'user_name': user.username if user else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Project(Model):
    """项目表"""
    id = fields.IntField(pk=True)
    opportunity = fields.ForeignKeyField('models.Opportunity', related_name='projects', description='关联商机')
    community_name = fields.CharField(max_length=200, description='小区名称')
    address = fields.CharField(max_length=500, description='具体房屋地址')
    contract_price = fields.DecimalField(max_digits=12, decimal_places=2, description='签约价格',
                                       validators=[MinValueValidator(0), MaxValueValidator(1000000000)])
    contract_period = fields.IntField(description='签约周期(天)',
                                    validators=[MinValueValidator(1), MaxValueValidator(3650)])
    signer = fields.CharField(max_length=100, description='签约人')
    delivery_date = fields.DatetimeField(null=True, description='交房日期')
    current_phase = fields.CharField(max_length=50, null=True, description='当前阶段')
    decoration_company = fields.CharField(max_length=200, null=True, description='装修公司')
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "project"
        table_description = "项目表"

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        # 获取商机数据
        opportunity_data = None
        print(f"[DEBUG] Project.to_dict - 开始转换项目 ID: {self.id}")
        try:
            print("[DEBUG] Project.to_dict - 尝试获取预加载的商机数据")
            opportunity = await self.opportunity
            print(f"[DEBUG] Project.to_dict - 成功获取商机: {opportunity.id if opportunity else None}")
            if opportunity:
                opportunity_data = {
                    "layout": opportunity.layout,
                    "area": opportunity.area,
                    "layout_image": opportunity.layout_image
                }
                print(f"[DEBUG] Project.to_dict - 商机数据: {opportunity_data}")
        except NoValuesFetched:
            print("[DEBUG] Project.to_dict - 商机数据未预加载，尝试重新查询")
            # 如果关联数据未预加载，则重新查询
            opportunity = await Opportunity.get_or_none(id=self.opportunity_id)
            print(f"[DEBUG] Project.to_dict - 重新查询商机结果: {opportunity.id if opportunity else None}")
            if opportunity:
                opportunity_data = {
                    "layout": opportunity.layout,
                    "area": opportunity.area,
                    "layout_image": opportunity.layout_image
                }
                print(f"[DEBUG] Project.to_dict - 重新查询获取的商机数据: {opportunity_data}")
        except Exception as e:
            print(f"[DEBUG] Project.to_dict - 获取商机数据时发生错误: {str(e)}")

        result = {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "community_name": self.community_name,
            "address": self.address,
            "contract_price": float(self.contract_price),  # 转换 Decimal 为 float
            "contract_period": self.contract_period,
            "signer": self.signer,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "current_phase": self.current_phase,
            "decoration_company": self.decoration_company,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # 添加商机信息
            "layout": opportunity_data["layout"] if opportunity_data else None,
            "area": opportunity_data["area"] if opportunity_data else None,
            "layout_image": opportunity_data["layout_image"] if opportunity_data else None
        }
        print(f"[DEBUG] Project.to_dict - 最终返回数据: {result}")
        return result

class ConstructionPhase(BaseModel, TimestampMixin):
    """施工阶段表"""
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField(
        'models.Project',
        related_name='phases',
        description='关联项目'
    )
    phase_type = fields.CharField(max_length=100, description='阶段类型')
    responsible = fields.CharField(max_length=100, null=True, description='负责人')
    notes = fields.TextField(null=True, description='备注')
    complete_time = fields.DatetimeField(null=True, description='完成时间')

    class Meta:
        table = "construction_phase"
        table_description = "施工阶段表"
        ordering = ["-created_at"]

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "phase_type": self.phase_type,
            "responsible": self.responsible,
            "notes": self.notes,
            "complete_time": self.complete_time.isoformat() if self.complete_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class PhaseMaterial(BaseModel, TimestampMixin):
    """阶段材料表"""
    id = fields.IntField(pk=True)
    phase = fields.ForeignKeyField('models.ConstructionPhase', related_name='phase_materials', description='关联施工阶段')
    material_type = fields.CharField(max_length=100, description='材料类型')
    file_path = fields.CharField(max_length=1000, description='文件路径')
    uploader = fields.CharField(max_length=100, description='上传人')

    class Meta:
        table = "phase_material"
        table_description = "阶段材料表"
        ordering = ["-created_at"]

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "phase_id": self.phase_id,
            "material_type": self.material_type,
            "file_path": self.file_path,
            "uploader": self.uploader,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None
        }

class ProjectMaterial(Model):
    """项目材料表"""
    id = fields.IntField(pk=True)
    project = fields.ForeignKeyField('models.Project', related_name='materials', description='关联项目')
    phase = fields.CharField(max_length=50, description='阶段类型')  # delivery/design/construction/completion
    file_type = fields.CharField(max_length=50, description='文件类型')  # image/cad/document
    material_type = fields.CharField(max_length=100, description='材料类型')  # 交房材料/设计图/CAD文件/报价单/现场照片
    file_url = fields.CharField(max_length=1000, description='文件URL')
    file_name = fields.CharField(max_length=200, description='原始文件名')
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = "project_material"
        table_description = "项目材料表"

    async def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "phase": self.phase,
            "file_type": self.file_type,
            "material_type": self.material_type,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }