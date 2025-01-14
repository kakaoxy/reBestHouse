from tortoise import fields
from tortoise.models import Model
from app.models.base import BaseModel, TimestampMixin
from datetime import datetime, date

class Community(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, description='小区名称')
    city = fields.CharField(max_length=50, null=False, default='shanghai', description='城市')
    region = fields.CharField(max_length=50, null=False, default='', description='区域')
    area = fields.CharField(max_length=50, null=False, default='', description='商圈')
    address = fields.CharField(max_length=200, null=True, description='地址')
    building_type = fields.CharField(max_length=50, null=True, description='建筑类型')
    property_rights = fields.CharField(max_length=100, null=True, description='交易权属')
    total_houses = fields.IntField(null=True, description='房屋总数')
    building_year = fields.IntField(null=True, description='建筑年代')
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
    community_name = fields.CharField(max_length=100)
    house_id = fields.CharField(max_length=50, null=True)  # 房源ID
    region = fields.CharField(max_length=50, null=True)  # 区域
    area = fields.CharField(max_length=50, null=True)  # 商圈
    layout = fields.CharField(max_length=50)  # 户型
    size = fields.FloatField()  # 面积
    floor = fields.CharField(max_length=50, null=True)  # 楼层描述
    floor_number = fields.IntField(null=True)  # 所在楼层
    total_floors = fields.IntField(null=True)  # 总楼层
    orientation = fields.CharField(max_length=50, null=True)  # 朝向
    ladder_ratio = fields.CharField(max_length=50, null=True)  # 梯户比
    total_price = fields.FloatField()  # 总价
    unit_price = fields.FloatField(null=True)  # 单价
    listing_date = fields.DateField(null=True)  # 挂牌时间
    last_transaction_date = fields.DateField(null=True)  # 上次交易时间
    mortgage_info = fields.CharField(max_length=200, null=True)  # 抵押信息
    layout_image = fields.CharField(max_length=500, null=True)  # 户型图链接
    ke_code = fields.CharField(max_length=50, null=True)  # 贝壳编号
    house_link = fields.CharField(max_length=500, null=True)  # 房源链接
    city = fields.CharField(max_length=50)  # 城市
    building_year = fields.IntField(null=True)  # 建筑年代
    building_structure = fields.CharField(max_length=50, null=True)  # 楼栋结构
    data_source = fields.CharField(max_length=50)  # 数据来源
    platform_listing_id = fields.CharField(max_length=50, null=True)  # 来源平台房源ID
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
            "house_id": self.house_id,
            "ke_code": self.ke_code,
            "house_link": self.house_link,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class DealRecord(BaseModel, TimestampMixin):
    id = fields.IntField(pk=True)
    house_id = fields.CharField(max_length=50, null=True, description='房源ID')
    community = fields.ForeignKeyField('models.Community', related_name='deal_records')
    community_name = fields.CharField(max_length=100, null=False, description='小区名称')
    region = fields.CharField(max_length=50, null=False, description='所在区域')
    area = fields.CharField(max_length=50, null=False, description='所在商圈')
    layout = fields.CharField(max_length=50, null=True, description='户型')
    size = fields.FloatField(null=False, description='建筑面积')
    floor_info = fields.CharField(max_length=50, null=True, description='楼层信息')
    floor_number = fields.IntField(null=True, description='所在楼层')
    total_floors = fields.IntField(null=True, description='总楼层')
    orientation = fields.CharField(max_length=50, null=True, description='房屋朝向')
    listing_price = fields.FloatField(null=True, description='挂牌价')
    total_price = fields.FloatField(null=False, description='成交价')
    unit_price = fields.FloatField(null=True, description='单价(元/平)')
    deal_date = fields.DateField(null=False, description='成交日期')
    deal_cycle = fields.IntField(null=True, description='成交周期')
    tags = fields.CharField(max_length=200, null=True, description='标签')
    layout_image = fields.CharField(max_length=500, null=True, description='户型图链接')
    house_link = fields.CharField(max_length=500, null=True, description='房源链接')
    city = fields.CharField(max_length=50, null=False, description='所在城市')
    building_year = fields.IntField(null=True, description='建筑年代')
    building_structure = fields.CharField(max_length=50, null=True, description='建筑结构')
    location = fields.CharField(max_length=200, null=True, description='位置')
    decoration = fields.CharField(max_length=50, null=True, description='装修')
    agency = fields.CharField(max_length=100, null=True, description='中介公司')
    source = fields.CharField(max_length=50, null=False, description='数据来源')
    source_transaction_id = fields.CharField(max_length=50, null=True, description='来源平台交易ID')
    entry_time = fields.DatetimeField(auto_now_add=True, description='数据入库时间')
    original_data = fields.JSONField(null=True, description='原始数据')

    # 标记为已废弃的字段
    data_source = fields.CharField(max_length=50, null=True, description='数据来源', deprecated=True)
    platform_listing_id = fields.CharField(max_length=50, null=True, description='平台房源ID', deprecated=True)

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
    community_name = fields.CharField(max_length=100, null=True)
    layout = fields.CharField(max_length=50, null=True)
    floor = fields.CharField(max_length=50, null=True)
    area = fields.FloatField(null=True)
    total_price = fields.FloatField(null=True)
    unit_price = fields.FloatField(null=True)
    address = fields.CharField(max_length=200, null=True)
    building_number = fields.CharField(max_length=50, null=True)
    room_number = fields.CharField(max_length=50, null=True)
    is_full_five = fields.BooleanField(default=False)
    is_full_two = fields.BooleanField(default=False)
    is_unique = fields.BooleanField(default=False)
    transaction_source = fields.CharField(max_length=50, null=True)
    layout_image = fields.CharField(max_length=500, null=True)
    interior_image = fields.CharField(max_length=500, null=True)
    location_image = fields.CharField(max_length=500, null=True)
    opportunity_owner = fields.CharField(max_length=100, null=True)
    belonging_owner = fields.CharField(max_length=100, null=True)
    status = fields.CharField(max_length=20, default='待评估')
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
    follow_up_method = fields.CharField(max_length=20, description='跟进方式')
    follow_up_content = fields.TextField(description='跟进内容')
    authorized_price = fields.FloatField(
        null=True,
        description='本次授权价格'
    )
    price_adjusted = fields.BooleanField(default=False, description='价格是否调整')
    adjust_reason = fields.TextField(null=True, description='价格调整原因')
    follow_up_result = fields.CharField(max_length=20, description='跟进结果')
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