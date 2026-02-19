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

# ============= 智慧农业新增模块 =============

class CropGrowthModel(Base):
    """农作物生长模型 - 智能决策系统"""
    __tablename__ = "crop_growth_models"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False, comment="作物名称")
    crop_type = Column(String(50), comment="作物类型: 水稻/蔬菜/水果/茶叶等")
    growth_stages = Column(Text, comment="生长阶段JSON: 播种->出苗->分蘖->抽穗->灌浆->成熟")
    base_temp = Column(Float, default=10, comment="基础积温(°C)")
    optimal_temp_min = Column(Float, default=20, comment="最适温度下限")
    optimal_temp_max = Column(Float, default=30, comment="最适温度上限")
    optimal_humidity_min = Column(Float, default=60, comment="最适湿度下限")
    optimal_humidity_max = Column(Float, default=80, comment="最适湿度上限")
    water_requirement = Column(Float, default=500, comment="全生育期需水量(mm)")
    fertilizer_requirement = Column(Float, default=0, comment="施肥量(kg/亩)")
    expected_yield = Column(Float, default=0, comment="预期产量(斤/亩)")
    prediction_accuracy = Column(Float, default=95, comment="预测准确率(%)")
    model_version = Column(String(20), default="v1.0", comment="模型版本")
    status = Column(String(20), default="active", comment="状态: active/inactive")
    description = Column(Text, comment="模型描述")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class DecisionRecord(Base):
    """智能决策记录 - 智慧决策输出"""
    __tablename__ = "decision_records"
    
    id = Column(Integer, primary_key=True, index=True)
    land_id = Column(Integer, nullable=True, comment="关联地块ID")
    crop_model_id = Column(Integer, nullable=True, comment="作物模型ID")
    decision_type = Column(String(50), nullable=False, comment="决策类型: 灌溉/施肥/喷药/收获预警")
    current_value = Column(Float, comment="当前值")
    recommended_value = Column(Float, comment="推荐值")
    recommendation = Column(Text, comment="决策建议")
    visualization_data = Column(Text, comment="可视化数据JSON(热力图/处方图)")
    confidence = Column(Float, default=0.95, comment="决策置信度")
    executed = Column(Boolean, default=False, comment="是否已执行")
    executed_at = Column(DateTime, comment="执行时间")
    created_at = Column(DateTime, server_default=func.now())

class TraceabilityRecord(Base):
    """全产业链追溯记录"""
    __tablename__ = "traceability_records"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), nullable=False, comment="产品名称")
    product_batch = Column(String(50), comment="产品批次号")
    category = Column(String(50), comment="产品分类")
    origin_farm = Column(String(100), comment="产地农场")
    origin_address = Column(String(200), comment="产地地址")
    planting_date = Column(String(20), comment="播种日期")
    harvest_date = Column(String(20), comment="收获日期")
    processing_date = Column(String(20), comment="加工日期")
    processing_factory = Column(String(100), comment="加工厂")
    logistics_company = Column(String(100), comment="物流公司")
    logistics_no = Column(String(100), comment="物流单号")
    warehouse = Column(String(100), comment="仓储地点")
    retail_outlet = Column(String(100), comment="零售终端")
    sale_date = Column(String(20), comment="销售日期")
    certifications = Column(Text, comment="认证信息JSON: 有机/绿色/地理标志")
    inspection_report = Column(Text, comment="检测报告JSON")
    trace_code = Column(String(100), unique=True, comment="追溯码")
    qr_code = Column(String(200), comment="二维码URL")
    status = Column(String(20), default="active", comment="状态: active/sold/offline")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class TraceabilityNode(Base):
    """追溯节点 - 记录每个环节"""
    __tablename__ = "traceability_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_record_id = Column(Integer, nullable=False, comment="追溯记录ID")
    node_type = Column(String(50), nullable=False, comment="节点类型: 播种/施肥/灌溉/采收/加工/物流/仓储/销售")
    node_name = Column(String(100), comment="节点名称")
    description = Column(Text, comment="环节描述")
    operator = Column(String(50), comment="操作人")
    location = Column(String(200), comment="位置")
    data = Column(Text, comment="环节数据JSON: 温度/湿度/操作记录等")
    image_url = Column(String(200), comment="现场图片URL")
    timestamp = Column(String(30), comment="时间戳")
    created_at = Column(DateTime, server_default=func.now())
