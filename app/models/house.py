from tortoise import fields
from tortoise.models import Model

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
    house_id = fields.CharField(max_length=50, null=True, description='房源ID')
    community_name = fields.CharField(max_length=100, null=True, description='小区名')
    region = fields.CharField(max_length=50, null=True, description='区域')
    area = fields.CharField(max_length=50, null=True, description='商圈')
    layout = fields.CharField(max_length=50, null=True, description='户型描述')
    size = fields.FloatField(null=True, description='建筑面积')
    floor = fields.CharField(max_length=50, null=True, description='楼层信息')
    orientation = fields.CharField(max_length=50, null=True, description='房屋朝向')
    ladder_ratio = fields.CharField(max_length=20, null=True, description='梯户比')
    total_price = fields.FloatField(null=False, description='房源总价')
    unit_price = fields.FloatField(null=True, description='房源单价')
    listing_date = fields.DatetimeField(null=True, description='挂牌时间')
    last_transaction_date = fields.DatetimeField(null=True, description='上次交易时间')
    mortgage_info = fields.CharField(max_length=200, null=True, description='抵押信息')
    layout_image = fields.CharField(max_length=500, null=True, description='户型图链接')
    ke_code = fields.CharField(max_length=50, null=True, description='贝壳编号')
    house_link = fields.CharField(max_length=500, null=True, description='房源链接')
    city = fields.CharField(max_length=50, null=True, description='城市')
    building_year = fields.IntField(null=True, description='建筑年代')
    building_structure = fields.CharField(max_length=50, null=True, description='楼栋结构')
    data_source = fields.CharField(max_length=20, null=False, description='数据来源')
    platform_listing_id = fields.CharField(max_length=50, null=True, description='来源平台房源ID')
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')
    floor_number = fields.IntField(null=True, description='楼层')
    total_floors = fields.IntField(null=True, description='总楼层')

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

class DealRecord(Model):
    id = fields.IntField(pk=True)
    community = fields.ForeignKeyField('models.Community', related_name='deal_records')
    source = fields.CharField(max_length=20, null=False, description='数据来源')
    source_transaction_id = fields.CharField(max_length=50, null=True, description='来源平台交易ID')
    deal_date = fields.DateField(null=False, description='成交日期')
    total_price = fields.FloatField(null=False, description='成交总价')
    unit_price = fields.FloatField(null=False, description='成交单价')
    layout = fields.CharField(max_length=50, null=True, description='户型')
    size = fields.FloatField(null=True, description='建筑面积')
    floor_info = fields.CharField(max_length=50, null=True, description='楼层信息')
    orientation = fields.CharField(max_length=50, null=True, description='房屋朝向')
    building_year = fields.IntField(null=True, description='建筑年代')
    agency = fields.CharField(max_length=100, null=True, description='中介公司')
    deal_cycle = fields.IntField(null=True, description='成交周期')
    house_link = fields.CharField(max_length=500, null=True, description='房源链接')
    layout_image = fields.CharField(max_length=500, null=True, description='户型图链接')
    entry_time = fields.DatetimeField(null=True, description='数据入库时间')
    original_data = fields.JSONField(null=True, description='原始数据')
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = "deal_record"
        table_description = "成交记录表"
        app = "models"

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