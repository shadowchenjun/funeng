"""
模型初始化
"""
from app.models.base import Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.uploaded_file import UploadedFile
from app.models.export_task import ExportTaskRecord
from app.models.cold_chain import (
    Transport, Vehicle, CargoOwner, ColdChainWarehouse,
    StorageZone, QualityInspection, InventoryRule, InventoryAlert,
    InboundAppointment, InboundOrder, InboundOrderItem, Operator, OperationTask, OperationBatch,
    TemperatureSensor, TemperatureReading, TemperatureAlert, OperatingCost,
)
from app.models.supply_chain_finance import FinancingOrder, Receivable, InsurancePolicy, CreditAssessment
from app.models.smart_agriculture import (
    EnvironmentReading, IrrigationZone, IrrigationRecord, MarketingOrder, MarketingTrafficDaily
)
from app.models.admin import (
    AdminUser, AdminRole,
    LandParcel, AdoptionCategory, AdoptionConfig, AdoptionOrder, RentalOrder,
    DeviceType, Device, MonitoringPoint, MonitoringRecord, DeviceLog,
    TraceabilityConfig, TraceabilityNode, TraceabilityRecordEntry,
    UserGroup, Coupon, Activity, SystemConfig, AdminOperationLog
)

__all__ = [
    "Base", "User", "Category", "Product", "UploadedFile", "ExportTaskRecord",
    "Transport", "Vehicle", "CargoOwner", "ColdChainWarehouse",
    "StorageZone", "QualityInspection", "InventoryRule", "InventoryAlert",
    "InboundAppointment", "InboundOrder", "InboundOrderItem", "Operator", "OperationTask", "OperationBatch",
    "TemperatureSensor", "TemperatureReading", "TemperatureAlert", "OperatingCost",
    "FinancingOrder", "Receivable", "InsurancePolicy", "CreditAssessment",
    "EnvironmentReading", "IrrigationZone", "IrrigationRecord", "MarketingOrder", "MarketingTrafficDaily",
    "AdminUser", "AdminRole",
    "LandParcel", "AdoptionCategory", "AdoptionConfig", "AdoptionOrder", "RentalOrder",
    "DeviceType", "Device", "MonitoringPoint", "MonitoringRecord", "DeviceLog",
    "TraceabilityConfig", "TraceabilityNode", "TraceabilityRecordEntry",
    "UserGroup", "Coupon", "Activity", "SystemConfig", "AdminOperationLog"
]
