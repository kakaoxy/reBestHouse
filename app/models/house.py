from tortoise import fields
from tortoise.models import Model

class Community(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, description='小区名称')
    region = fields.CharField(max_length=50, null=True, description='区域')
    area = fields.CharField(max_length=50, null=True, description='商圈')
    address = fields.CharField(max_length=200, null=True, description='地址')
    building_type = fields.CharField(max_length=50, null=True, description='建筑类型')
    property_rights = fields.CharField(max_length=50, null=True, description='交易权属')
    total_houses = fields.IntField(null=True, description='房屋总数')
    building_year = fields.IntField(null=True, description='建筑年代')
    created_at = fields.DatetimeField(auto_now_add=True, description='创建时间')
    updated_at = fields.DatetimeField(auto_now=True, description='更新时间')

    # 反向关系
    houses: fields.ReverseRelation["Ershoufang"]

    class Meta:
        table = "community"

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