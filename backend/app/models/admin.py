"""
管理员模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(500), nullable=True)
    role_id = Column(Integer, ForeignKey("admin_roles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    role = relationship("AdminRole", back_populates="users")


class AdminRole(Base):
    __tablename__ = "admin_roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    users = relationship("AdminUser", back_populates="role")


# ============ 土地与认养模型 ============

class LandParcel(Base):
    __tablename__ = "land_parcels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    area = Column(Float, nullable=False)  # 面积（平方米）
    location = Column(String(200), nullable=True)  # 位置
    status = Column(String(20), default="available")  # available, rented, reserved
    type = Column(String(20), default="farm")  # farm, orchard, greenhouse
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AdoptionCategory(Base):
    __tablename__ = "adoption_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    configs = relationship("AdoptionConfig", back_populates="category")


class AdoptionConfig(Base):
    __tablename__ = "adoption_configs"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("adoption_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    unit = Column(String(20), default="year")  # year, month, season
    duration_days = Column(Integer, nullable=False)  # 认养时长（天）
    benefits = Column(Text, nullable=True)  # JSON string
    images = Column(Text, nullable=True)  # JSON array of image URLs
    is_active = Column(Boolean, default=True)
    stock = Column(Integer, default=0)  # 可用库存
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    category = relationship("AdoptionCategory", back_populates="configs")


class AdoptionOrder(Base):
    __tablename__ = "adoption_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    config_id = Column(Integer, ForeignKey("adoption_configs.id"), nullable=False)
    land_parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=True)
    quantity = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, active, completed, cancelled, refunded
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    harvest_info = Column(Text, nullable=True)  # JSON string
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User")
    config = relationship("AdoptionConfig")
    land_parcel = relationship("LandParcel")


class RentalOrder(Base):
    __tablename__ = "rental_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    land_parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=False)
    area = Column(Float, nullable=False)  # 租用面积
    unit_price = Column(Float, nullable=False)  # 单价
    total_amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, active, completed, cancelled, refunded
    crop_plan = Column(Text, nullable=True)  # 种植计划
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User")
    land_parcel = relationship("LandParcel")


# ============ 设备模型 ============

class DeviceType(Base):
    __tablename__ = "device_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    devices = relationship("Device", back_populates="device_type")


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    device_type_id = Column(Integer, ForeignKey("device_types.id"), nullable=False)
    land_parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(String(20), default="online")  # online, offline, error, maintenance
    last_active = Column(DateTime, nullable=True)
    config = Column(Text, nullable=True)  # JSON string
    firmware_version = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    device_type = relationship("DeviceType", back_populates="devices")
    land_parcel = relationship("LandParcel")
    monitoring_points = relationship("MonitoringPoint", back_populates="device")
    logs = relationship("DeviceLog", back_populates="device")


class MonitoringPoint(Base):
    __tablename__ = "monitoring_points"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    name = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)  # temperature, humidity, soil_moisture, etc.
    unit = Column(String(20), nullable=True)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    device = relationship("Device", back_populates="monitoring_points")
    records = relationship("MonitoringRecord", back_populates="monitoring_point")


class MonitoringRecord(Base):
    __tablename__ = "monitoring_records"

    id = Column(Integer, primary_key=True, index=True)
    monitoring_point_id = Column(Integer, ForeignKey("monitoring_points.id"), nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    monitoring_point = relationship("MonitoringPoint", back_populates="records")


class DeviceLog(Base):
    __tablename__ = "device_logs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    log_type = Column(String(50), nullable=False)  # error, warning, info, upgrade
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    device = relationship("Device", back_populates="logs")


# ============ 溯源模型 ============

class TraceabilityConfig(Base):
    __tablename__ = "traceability_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    land_parcel_id = Column(Integer, ForeignKey("land_parcels.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    nodes = relationship("TraceabilityNode", back_populates="config")


class TraceabilityNode(Base):
    __tablename__ = "traceability_nodes"

    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("traceability_configs.id"), nullable=False)
    name = Column(String(100), nullable=False)
    node_type = Column(String(50), nullable=False)  # planting, growing, harvesting, processing, packaging, transport
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    sort_order = Column(Integer, default=0)
    data_fields = Column(Text, nullable=True)  # JSON string defining what data to capture
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    config = relationship("TraceabilityConfig", back_populates="nodes")
    records = relationship("TraceabilityRecordEntry", back_populates="node")


class TraceabilityRecordEntry(Base):
    __tablename__ = "traceability_record_entries"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("traceability_nodes.id"), nullable=False)
    adoption_order_id = Column(Integer, ForeignKey("adoption_orders.id"), nullable=True)
    data = Column(Text, nullable=False)  # JSON string of record data
    image_url = Column(String(500), nullable=True)
    operator = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)

    node = relationship("TraceabilityNode", back_populates="records")
    adoption_order = relationship("AdoptionOrder")


# ============ 营销模型 ============

class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    criteria = Column(Text, nullable=True)  # JSON string defining membership criteria
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    type = Column(String(20), default="discount")  # discount, cash
    discount_value = Column(Float, nullable=False)  # 折扣金额或折扣率
    min_amount = Column(Float, default=0)  # 最低消费金额
    max_discount = Column(Float, nullable=True)  # 最高折扣金额
    total_count = Column(Integer, default=0)
    used_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    applicable_products = Column(Text, nullable=True)  # JSON array of product IDs, null means all
    applicable_categories = Column(Text, nullable=True)  # JSON array of category IDs
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # flash_sale, group_buy, sign_in, etc.
    description = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)  # JSON string
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, active, ended, cancelled
    banner_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ============ 系统配置模型 ============

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    type = Column(String(20), default="string")  # string, number, boolean, json
    group = Column(String(50), default="general")  # general, site, payment, etc.
    description = Column(String(200), nullable=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# ============ 操作日志 ============

class AdminOperationLog(Base):
    __tablename__ = "admin_operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    detail = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    admin_user = relationship("AdminUser")
