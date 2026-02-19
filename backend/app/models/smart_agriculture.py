"""
智慧农业相关数据模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base

class Land(Base):
    """地块模型"""
    __tablename__ = "lands"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, nullable=True, index=True, comment="所属农场ID")
    name = Column(String(100), nullable=False, comment="地块名称")
    area = Column(Float, default=0, comment="面积(亩)")
    crop = Column(String(100), comment="种植作物(单个)")
    crops = Column(Text, comment="关联作物(多个,逗号分隔)")  # 新增：多对多关系
    status = Column(String(20), default="normal", comment="状态: normal/warning")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Crop(Base):
    """作物模型"""
    __tablename__ = "crops"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="作物名称")
    category = Column(String(50), comment="分类: 粮食/蔬菜/水果/其他")
    planting_season = Column(String(50), comment="种植季节")
    growth_days = Column(Integer, default=0, comment="生长周期(天)")
    yield_per_mu = Column(Float, default=0, comment="亩产量(斤)")
    status = Column(String(20), default="active", comment="状态: active/inactive")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class FarmInfo(Base):
    """农场信息模型"""
    __tablename__ = "farm_info"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="农场名称")
    address = Column(String(200), comment="农场地址")
    lat = Column(Float, nullable=True, comment="纬度")
    lng = Column(Float, nullable=True, comment="经度")
    total_area = Column(Float, default=0, comment="总面积(亩)")
    manager = Column(String(50), comment="负责人")
    phone = Column(String(20), comment="联系电话")
    coords = Column(String(50), comment="坐标")
    status = Column(String(20), default="normal", comment="状态: normal/warning")
    description = Column(Text, comment="农场描述")
    established_date = Column(String(20), comment="成立日期")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class IoTDevice(Base):
    """物联网设备模型"""
    __tablename__ = "iot_devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="设备名称")
    # 设备类型: temp/humidity/soil/weather/camera/pest_lamp/leaf_sensor/water_fertilizer/control_valve
    device_type = Column(String(50), comment="设备类型")
    location = Column(String(100), comment="安装位置")
    land_id = Column(Integer, nullable=True, comment="关联地块ID")  # 新增：关联地块
    status = Column(String(20), default="online", comment="状态: online/offline/warning")
    last_update = Column(DateTime, comment="最后更新时间")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Warehouse(Base):
    """冷链仓库模型"""
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="仓库名称")
    address = Column(String(200), comment="仓库地址")
    capacity = Column(Float, default=0, comment="容量(m³)")
    area = Column(Float, default=0, comment="面积(㎡)")
    temperature = Column(Float, default=-18, comment="温度(°C)")
    humidity = Column(Float, default=45, comment="湿度(%)")
    inventory = Column(Integer, default=0, comment="库存数量")
    status = Column(String(20), default="正常", comment="状态")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Member(Base):
    """会员模型"""
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), comment="电话")
    level = Column(String(20), default="普通", comment="会员等级")
    points = Column(Integer, default=0, comment="积分")
    total_spent = Column(String(50), default="¥0", comment="累计消费")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Campaign(Base):
    """营销活动模型"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="活动名称")
    campaign_type = Column(String(50), comment="活动类型")
    status = Column(String(20), default="未开始", comment="状态")
    participants = Column(Integer, default=0, comment="参与人数")
    sales = Column(String(50), default="¥0", comment="销售额")
    end_date = Column(String(20), comment="结束日期")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
