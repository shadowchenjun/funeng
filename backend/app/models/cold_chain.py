"""
冷链运输模型
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime


class Transport(Base):
    """运输记录表"""
    __tablename__ = "transports"

    id = Column(String, primary_key=True, index=True)
    vehicle_no = Column(String, nullable=False, index=True)  # 车牌号
    driver = Column(String)  # 司机
    route = Column(String)  # 路线描述 如"北京-上海"
    start_city = Column(String)  # 出发城市
    end_city = Column(String)  # 目的城市
    status = Column(String, default="waiting")  # waiting/in_transit/arrived
    temperature = Column(Float)  # 当前温度
    humidity = Column(Float)  # 当前湿度
    speed = Column(Float)  # 速度 km/h
    fuel = Column(Float)  # 油量百分比
    cargo = Column(String)  # 货物类型
    weight = Column(Float)  # 重量吨
    current_lat = Column(Float)  # 当前纬度
    current_lng = Column(Float)  # 当前经度
    current_location = Column(String)  # 当前位置描述
    departure_time = Column(DateTime)  # 出发时间
    eta = Column(DateTime)  # 预计到达时间
    waypoints = Column(JSON)  # 途经点坐标 [{"lat": 36.65, "lng": 117.12, "name": "济南"}, ...]
    route_coords = Column(JSON)  # 完整路线坐标 [[lng, lat], ...]
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Warehouse 模型定义在 smart_agriculture.py，cold_chain API 通过 ORM 访问。


class Vehicle(Base):
    """冷藏车辆表"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plate = Column(String(20), nullable=False)  # 车牌号
    vehicle_type = Column(String(50), default="冷藏车")
    driver = Column(String(50))
    phone = Column(String(20))
    load_capacity = Column(Float, default=5)  # 载重(吨)
    volume = Column(Float)  # 容积(m³)
    gps_device = Column(String(50))
    temp_range = Column(String(20), default="-25°C~5°C")
    status = Column(String(20), default="空闲")
    location = Column(String(100))
    temperature = Column(Float, default=-18)
    battery = Column(Float, default=100)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CargoOwner(Base):
    """货主表"""
    __tablename__ = "cargo_owners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)  # 货主编码
    name = Column(String(100), nullable=False)
    contact = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    status = Column(String(20), default="正常")
    created_at = Column(DateTime, default=datetime.now)


# ========== WMS 业务实体（全部由 ORM 管理，create_all 自动建表） ==========


class StorageZone(Base):
    """仓库温区（库区）"""
    __tablename__ = "cold_chain_zones"

    id = Column(String(20), primary_key=True)  # Z0001
    code = Column(String(10), nullable=False)  # 库区字母，用于生成货位号 A/B/C...
    name = Column(String(50), nullable=False)  # 冷藏区A
    type = Column(String(20), nullable=False)  # 冷藏区/冷冻区/常温区/恒温区
    warehouse = Column(String(100), nullable=False)  # 所属仓库名称
    owner_code = Column(String(20))  # 租用该温区的货主编码（可空 = 公共区）
    temperature_min = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)  # 容量（托位）
    used = Column(Integer, default=0)  # 已占用托位
    distance_to_pick = Column(Integer, default=10)  # 距拣货/出库口距离(米)
    status = Column(String(20), default="正常")  # 正常/维护中


class QualityInspection(Base):
    """品控检查记录"""
    __tablename__ = "cold_chain_quality_inspections"

    id = Column(String(20), primary_key=True)  # QC00001
    type = Column(String(20), nullable=False)
    product = Column(String(100), nullable=False)
    batch_no = Column(String(50), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    result = Column(String(20), nullable=False)  # 合格/待复检/不合格
    score = Column(Float, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    pesticide_residue = Column(Float)
    heavy_metal = Column(Float)
    inspector = Column(String(50))
    location = Column(String(100))
    remark = Column(String(200))
    items = Column(JSON)  # 检查项明细 [{"name","result","score"}]
    created_at = Column(DateTime, default=datetime.now)


class InventoryRule(Base):
    """库存预警规则"""
    __tablename__ = "cold_chain_inventory_rules"

    id = Column(String(20), primary_key=True)  # RULE001
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)
    threshold = Column(Float, nullable=False)
    unit = Column(String(10))
    product_categories = Column(JSON)
    notify_channels = Column(JSON)


class InventoryAlert(Base):
    """库存预警"""
    __tablename__ = "cold_chain_inventory_alerts"

    id = Column(String(20), primary_key=True)  # IA0001
    type = Column(String(20), nullable=False)  # 库存不足/库存过多/临期预警/温度异常/湿度异常
    level = Column(String(20), nullable=False)  # low/medium/high/critical
    product = Column(String(100), nullable=False)
    product_code = Column(String(20))
    warehouse = Column(String(100))
    zone = Column(String(50))
    current_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    unit = Column(String(10))
    status = Column(String(20), default="待处理")  # 待处理/处理中/已确认/已解决
    resolve_remark = Column(String(200))
    created_at = Column(DateTime, default=datetime.now)
    resolved_at = Column(DateTime)


class InboundAppointment(Base):
    """入库预约"""
    __tablename__ = "cold_chain_inbound_appointments"

    id = Column(String(30), primary_key=True)  # INB2026090001
    owner = Column(String(100), nullable=False)
    owner_code = Column(String(20))
    vehicle_no = Column(String(20), nullable=False)
    driver = Column(String(50))
    driver_phone = Column(String(20))
    estimated_arrival = Column(DateTime, nullable=False)
    actual_arrival = Column(DateTime)
    dock = Column(String(10))
    zone = Column(String(50))
    cargo_type = Column(String(50))
    remark = Column(String(200))
    items = Column(JSON)  # 预约货物 [{"sku","name","quantity","unit","barcode","storage_type"}]
    status = Column(String(20), default="待签到")  # 待签到/已签到/收货中/已完成
    created_at = Column(DateTime, default=datetime.now)


class InboundOrder(Base):
    """入库单"""
    __tablename__ = "cold_chain_inbound_orders"

    id = Column(String(30), primary_key=True)  # IOR2026090001
    appointment_id = Column(String(30))
    owner = Column(String(100), nullable=False)
    warehouse = Column(String(100))
    inbound_date = Column(String(10))
    status = Column(String(20), default="待收货")  # 待收货/收货中/已入库/已质检
    dock = Column(String(10))
    receiver = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)

    items = relationship("InboundOrderItem", back_populates="order", order_by="InboundOrderItem.id",
                         cascade="all, delete-orphan")


class InboundOrderItem(Base):
    """入库单货物明细"""
    __tablename__ = "cold_chain_inbound_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(30), ForeignKey("cold_chain_inbound_orders.id"), nullable=False, index=True)
    sku = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    barcode = Column(String(30))
    storage_type = Column(String(10), nullable=False)  # 冷藏/冷冻/常温
    expected_qty = Column(Integer, nullable=False)
    received_qty = Column(Integer, default=0)
    qualified_qty = Column(Integer, default=0)
    zone_id = Column(String(20))  # 上架后的温区
    location = Column(String(30))  # 上架后的货位

    order = relationship("InboundOrder", back_populates="items")


class Operator(Base):
    """仓库作业人员"""
    __tablename__ = "cold_chain_operators"

    employee_id = Column(String(20), primary_key=True)  # EMP0001
    name = Column(String(50), nullable=False)
    department = Column(String(20), nullable=False)


class OperationTask(Base):
    """作业任务"""
    __tablename__ = "cold_chain_operation_tasks"

    id = Column(String(20), primary_key=True)  # TSK00001
    type = Column(String(10), nullable=False)
    priority = Column(String(10), nullable=False)  # 紧急/高/普通/低
    status = Column(String(10), default="待执行")  # 待执行/执行中/已完成/已取消
    owner = Column(String(100))
    location = Column(String(30))
    target_location = Column(String(30))
    quantity = Column(Integer, nullable=False)
    assigned_to = Column(String(50))  # Operator.name
    assigned_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    barcode = Column(String(30))
    error_count = Column(Integer, default=0)
    batch_id = Column(String(30))
    items = Column(JSON)  # [{"sku","name","barcode","quantity","location"}]
    history = Column(JSON)  # [{"action","operator","time","detail"?}]


class OperationBatch(Base):
    """拣货批次"""
    __tablename__ = "cold_chain_operation_batches"

    id = Column(String(30), primary_key=True)  # BATCH202609290001
    zone = Column(String(20))
    task_ids = Column(JSON, nullable=False)
    status = Column(String(10), default="待执行")
    created_at = Column(DateTime, default=datetime.now)


class TemperatureSensor(Base):
    """温度传感器（冷库/冷藏车）"""
    __tablename__ = "cold_chain_sensors"

    id = Column(String(20), primary_key=True)  # SEN101
    name = Column(String(100), nullable=False)  # 北京冷链中心-冷冻库 / 冷藏车 京A12345
    location = Column(String(100))  # 地址或路段
    kind = Column(String(10), default="冷库")  # 冷库/冷藏车
    target_temp = Column(Float, nullable=False)
    tolerance = Column(Float, default=2.0)  # 允许偏差(°C)


class TemperatureReading(Base):
    """传感器温湿度读数（IoT 上报）"""
    __tablename__ = "cold_chain_temperature_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(20), ForeignKey("cold_chain_sensors.id"), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float)
    recorded_at = Column(DateTime, nullable=False, index=True)


class TemperatureAlert(Base):
    """温度告警"""
    __tablename__ = "cold_chain_temperature_alerts"

    id = Column(String(20), primary_key=True)  # A0001
    sensor_id = Column(String(20), nullable=False)
    location = Column(String(100))
    type = Column(String(20), default="温度异常")
    temperature = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    severity = Column(String(10), nullable=False)  # warning/critical
    status = Column(String(10), default="未处理")  # 未处理/处理中/已解决
    message = Column(String(200))
    timestamp = Column(DateTime, default=datetime.now)


class OperatingCost(Base):
    """冷链运营成本（按月、按类别）"""
    __tablename__ = "cold_chain_operating_costs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False)  # 2026-09
    category = Column(String(20), nullable=False)  # electricity/fuel/maintenance
    amount = Column(Float, nullable=False)


# ========== 迁移兼容 ==========


class ColdChainWarehouse(Base):
    """Legacy table retained so an existing database can be migrated losslessly."""

    __tablename__ = "cold_chain_warehouses"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    capacity = Column(Float)
    used = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
