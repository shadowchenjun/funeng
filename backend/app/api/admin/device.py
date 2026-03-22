"""
设备管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
import json

from app.database import get_db
from app.models.admin import (
    AdminUser, DeviceType, Device, MonitoringPoint, MonitoringRecord, DeviceLog
)
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


# ============ 设备类型 ============

@router.get("/types")
def list_device_types(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取设备类型列表"""
    types = db.query(DeviceType).order_by(DeviceType.id).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "code": t.code,
            "icon": t.icon,
            "description": t.description,
            "specifications": json.loads(t.specifications) if t.specifications else None,
            "is_active": t.is_active,
            "created_at": t.created_at
        }
        for t in types
    ]


@router.post("/types")
def create_device_type(
    name: str,
    code: str,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    specifications: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建设备类型"""
    existing = db.query(DeviceType).filter(DeviceType.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备类型代码已存在")

    device_type = DeviceType(
        name=name,
        code=code,
        icon=icon,
        description=description,
        specifications=specifications
    )
    db.add(device_type)
    db.commit()
    db.refresh(device_type)

    log_operation(db, current_admin.id, "create", "device_type", device_type.id, f"创建设备类型: {name}")

    return {"id": device_type.id, "message": "创建成功"}


@router.put("/types/{type_id}")
def update_device_type(
    type_id: int,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    specifications: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新设备类型"""
    device_type = db.query(DeviceType).filter(DeviceType.id == type_id).first()
    if not device_type:
        raise HTTPException(status_code=404, detail="设备类型不存在")

    if name:
        device_type.name = name
    if icon:
        device_type.icon = icon
    if description:
        device_type.description = description
    if specifications:
        device_type.specifications = specifications
    if is_active is not None:
        device_type.is_active = is_active

    device_type.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "device_type", type_id, f"更新设备类型: {name}")

    return {"message": "更新成功"}


@router.delete("/types/{type_id}")
def delete_device_type(
    type_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除设备类型"""
    device_type = db.query(DeviceType).filter(DeviceType.id == type_id).first()
    if not device_type:
        raise HTTPException(status_code=404, detail="设备类型不存在")

    # 检查是否有设备关联
    devices = db.query(Device).filter(Device.device_type_id == type_id).count()
    if devices > 0:
        raise HTTPException(status_code=400, detail="该类型下有设备，无法删除")

    db.delete(device_type)
    db.commit()

    log_operation(db, current_admin.id, "delete", "device_type", type_id, f"删除设备类型")

    return {"message": "删除成功"}


# ============ 设备 ============

@router.get("/devices")
def list_devices(
    device_type_id: Optional[int] = None,
    land_parcel_id: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取设备列表"""
    query = db.query(Device)

    if device_type_id:
        query = query.filter(Device.device_type_id == device_type_id)
    if land_parcel_id:
        query = query.filter(Device.land_parcel_id == land_parcel_id)
    if status:
        query = query.filter(Device.status == status)
    if keyword:
        query = query.filter(
            (Device.name.contains(keyword)) |
            (Device.code.contains(keyword)) |
            (Device.location.contains(keyword))
        )

    total = query.count()
    devices = query.order_by(Device.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": d.id,
                "name": d.name,
                "code": d.code,
                "device_type_id": d.device_type_id,
                "device_type_name": d.device_type.name if d.device_type else None,
                "land_parcel_id": d.land_parcel_id,
                "land_parcel_name": d.land_parcel.name if d.land_parcel else None,
                "location": d.location,
                "status": d.status,
                "last_active": d.last_active,
                "firmware_version": d.firmware_version,
                "created_at": d.created_at
            }
            for d in devices
        ]
    }


@router.get("/devices/{device_id}")
def get_device(
    device_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取设备详情"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 获取监控点
    monitoring_points = db.query(MonitoringPoint).filter(
        MonitoringPoint.device_id == device_id
    ).all()

    return {
        "id": device.id,
        "name": device.name,
        "code": device.code,
        "device_type_id": device.device_type_id,
        "device_type_name": device.device_type.name if device.device_type else None,
        "land_parcel_id": device.land_parcel_id,
        "land_parcel_name": device.land_parcel.name if device.land_parcel else None,
        "location": device.location,
        "status": device.status,
        "config": json.loads(device.config) if device.config else {},
        "firmware_version": device.firmware_version,
        "last_active": device.last_active,
        "created_at": device.created_at,
        "updated_at": device.updated_at,
        "monitoring_points": [
            {
                "id": mp.id,
                "name": mp.name,
                "data_type": mp.data_type,
                "unit": mp.unit,
                "threshold_min": mp.threshold_min,
                "threshold_max": mp.threshold_max,
                "is_active": mp.is_active
            }
            for mp in monitoring_points
        ]
    }


@router.post("/devices")
def create_device(
    name: str,
    code: str,
    device_type_id: int,
    location: Optional[str] = None,
    land_parcel_id: Optional[int] = None,
    config: Optional[str] = None,
    firmware_version: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建设备"""
    existing = db.query(Device).filter(Device.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="设备编号已存在")

    device_type = db.query(DeviceType).filter(DeviceType.id == device_type_id).first()
    if not device_type:
        raise HTTPException(status_code=404, detail="设备类型不存在")

    device = Device(
        name=name,
        code=code,
        device_type_id=device_type_id,
        location=location,
        land_parcel_id=land_parcel_id,
        config=config,
        firmware_version=firmware_version
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    log_operation(db, current_admin.id, "create", "device", device.id, f"创建设备: {name}")

    return {"id": device.id, "message": "创建成功"}


@router.put("/devices/{device_id}")
def update_device(
    device_id: int,
    name: Optional[str] = None,
    location: Optional[str] = None,
    land_parcel_id: Optional[int] = None,
    config: Optional[str] = None,
    firmware_version: Optional[str] = None,
    status: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新设备"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    if name:
        device.name = name
    if location:
        device.location = location
    if land_parcel_id is not None:
        device.land_parcel_id = land_parcel_id
    if config:
        device.config = config
    if firmware_version:
        device.firmware_version = firmware_version
    if status:
        device.status = status

    device.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "device", device_id, f"更新设备: {name}")

    return {"message": "更新成功"}


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除设备"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # 删除关联的监控点和日志
    db.query(MonitoringRecord).filter(
        MonitoringRecord.monitoring_point_id.in_(
            db.query(MonitoringPoint.id).filter(MonitoringPoint.device_id == device_id)
        )
    ).delete(synchronize_session=False)
    db.query(MonitoringPoint).filter(MonitoringPoint.device_id == device_id).delete()
    db.query(DeviceLog).filter(DeviceLog.device_id == device_id).delete()
    db.delete(device)
    db.commit()

    log_operation(db, current_admin.id, "delete", "device", device_id, f"删除设备")

    return {"message": "删除成功"}


# ============ 监控点 ============

@router.get("/monitoring-points")
def list_monitoring_points(
    device_id: Optional[int] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取监控点列表"""
    query = db.query(MonitoringPoint)
    if device_id:
        query = query.filter(MonitoringPoint.device_id == device_id)

    points = query.all()
    return [
        {
            "id": p.id,
            "device_id": p.device_id,
            "device_name": p.device.name if p.device else None,
            "name": p.name,
            "data_type": p.data_type,
            "unit": p.unit,
            "threshold_min": p.threshold_min,
            "threshold_max": p.threshold_max,
            "is_active": p.is_active,
            "created_at": p.created_at
        }
        for p in points
    ]


@router.post("/monitoring-points")
def create_monitoring_point(
    device_id: int,
    name: str,
    data_type: str,
    unit: Optional[str] = None,
    threshold_min: Optional[float] = None,
    threshold_max: Optional[float] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建监控点"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    point = MonitoringPoint(
        device_id=device_id,
        name=name,
        data_type=data_type,
        unit=unit,
        threshold_min=threshold_min,
        threshold_max=threshold_max
    )
    db.add(point)
    db.commit()
    db.refresh(point)

    return {"id": point.id, "message": "创建成功"}


@router.put("/monitoring-points/{point_id}")
def update_monitoring_point(
    point_id: int,
    name: Optional[str] = None,
    unit: Optional[str] = None,
    threshold_min: Optional[float] = None,
    threshold_max: Optional[float] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新监控点"""
    point = db.query(MonitoringPoint).filter(MonitoringPoint.id == point_id).first()
    if not point:
        raise HTTPException(status_code=404, detail="监控点不存在")

    if name:
        point.name = name
    if unit:
        point.unit = unit
    if threshold_min is not None:
        point.threshold_min = threshold_min
    if threshold_max is not None:
        point.threshold_max = threshold_max
    if is_active is not None:
        point.is_active = is_active

    db.commit()
    return {"message": "更新成功"}


# ============ 设备日志 ============

@router.get("/devices/{device_id}/logs")
def get_device_logs(
    device_id: int,
    log_type: Optional[str] = None,
    limit: int = 50,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取设备日志"""
    query = db.query(DeviceLog).filter(DeviceLog.device_id == device_id)
    if log_type:
        query = query.filter(DeviceLog.log_type == log_type)

    logs = query.order_by(DeviceLog.created_at.desc()).limit(limit).all()

    return [
        {
            "id": log.id,
            "log_type": log.log_type,
            "message": log.message,
            "created_at": log.created_at
        }
        for log in logs
    ]
