"""
模型初始化
"""
from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.cold_chain import Transport
from app.models.admin import (
    AdminUser, AdminRole,
    LandParcel, AdoptionCategory, AdoptionConfig, AdoptionOrder, RentalOrder,
    DeviceType, Device, MonitoringPoint, MonitoringRecord, DeviceLog,
    TraceabilityConfig, TraceabilityNode, TraceabilityRecordEntry,
    UserGroup, Coupon, Activity, SystemConfig, AdminOperationLog
)

__all__ = [
    "Base", "User", "Category", "Product",
    "Transport",
    "AdminUser", "AdminRole",
    "LandParcel", "AdoptionCategory", "AdoptionConfig", "AdoptionOrder", "RentalOrder",
    "DeviceType", "Device", "MonitoringPoint", "MonitoringRecord", "DeviceLog",
    "TraceabilityConfig", "TraceabilityNode", "TraceabilityRecordEntry",
    "UserGroup", "Coupon", "Activity", "SystemConfig", "AdminOperationLog"
]
