"""
数字冷链物联 API

所有业务数据（运输、仓库、车辆、货主、温区、品控、库存预警、入库预约/入库单、作业任务、
温度传感器读数与告警、运营成本）均持久化在数据库中，统计类接口由数据行实时计算，不使用随机数。
温湿度曲线来自 cold_chain_temperature_readings 表（IoT 上报；默认数据为种子写入的固定读数），
可通过 POST /monitoring/readings 写入新读数。
"""
import math
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Literal, Optional, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cold_chain import (
    CargoOwner, Vehicle, Transport,
    StorageZone, QualityInspection, InventoryRule, InventoryAlert,
    InboundAppointment, InboundOrder, InboundOrderItem, Operator, OperationTask, OperationBatch,
    TemperatureSensor, TemperatureReading, TemperatureAlert, OperatingCost,
)
from app.models.smart_agriculture import Warehouse, TraceabilityRecord

router = APIRouter()

UNITS_PER_PALLET = 50  # 1 个托位约容纳 50 件货物，用于温区容量换算
OUTBOUND_TASK_TYPES = ("拣货", "复核", "打包", "发货")
PRIORITY_ORDER = {"紧急": 0, "高": 1, "普通": 2, "低": 3}
LEVEL_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
# 货物存储条件 -> (首选温区类型, 可替代温区类型)
STORAGE_ZONE_TYPES = {"冷藏": ("冷藏区", "恒温区"), "冷冻": ("冷冻区", None), "常温": ("常温区", "恒温区")}


# ========== 通用工具 ==========

def _fmt(dt: Optional[datetime], seconds: bool = False) -> Optional[str]:
    if dt is None:
        return None
    if isinstance(dt, str):  # 兼容旧库中的字符串时间
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S" if seconds else "%Y-%m-%d %H:%M")


def _next_id(db: Session, model, prefix: str, width: int) -> str:
    """按前缀生成下一个顺序编号，例如 QC00021"""
    max_no = 0
    for (value,) in db.query(model.id).filter(model.id.like(f"{prefix}%")).all():
        suffix = value[len(prefix):]
        if suffix.isdigit():
            max_no = max(max_no, int(suffix))
    return f"{prefix}{max_no + 1:0{width}d}"


def _get_or_404(db: Session, model, key, label: str):
    obj = db.get(model, key)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{label}不存在")
    return obj


def _pct(part: float, whole: float) -> float:
    return round(part / whole * 100, 1) if whole else 0.0


# ========== 运输 ==========

def _transport_dict(t: Transport) -> dict:
    return {
        "id": t.id,
        "vehicle_no": t.vehicle_no,
        "driver": t.driver,
        "route": t.route,
        "start_city": t.start_city,
        "end_city": t.end_city,
        "status": t.status,
        "temperature": t.temperature,
        "humidity": t.humidity,
        "speed": t.speed,
        "fuel": t.fuel,
        "cargo": t.cargo,
        "weight": t.weight,
        "current_lat": t.current_lat,
        "current_lng": t.current_lng,
        "current_location": t.current_location,
        "departure_time": _fmt(t.departure_time, seconds=True),
        "eta": _fmt(t.eta, seconds=True),
        "waypoints": t.waypoints,
        "route_coords": t.route_coords,
    }


@router.get("/transport")
def get_transports(db: Session = Depends(get_db)):
    """获取运输列表"""
    rows = db.query(Transport).order_by(Transport.created_at.desc(), Transport.id).all()
    return [_transport_dict(t) for t in rows]


def _route_points(t: Transport) -> list:
    """根据途经点与车辆当前位置推导各节点状态，按出发/到达时间线性估算经过时间"""
    points = t.waypoints if isinstance(t.waypoints, list) else []
    if not points:
        return []
    n = len(points)
    if t.current_lat is not None and t.current_lng is not None:
        cur = min(range(n), key=lambda i: (points[i]["lat"] - t.current_lat) ** 2
                  + (points[i]["lng"] - t.current_lng) ** 2)
    else:
        cur = 0
    dep = t.departure_time if isinstance(t.departure_time, datetime) else None
    eta = t.eta if isinstance(t.eta, datetime) else None
    result = []
    for i, p in enumerate(points):
        if t.status == "arrived":
            status = "已到达" if i == n - 1 else "已通过"
        elif t.status == "waiting":
            status = "待出发" if i == 0 else "预计"
        else:
            status = "已通过" if i < cur else ("当前位置" if i == cur else "预计")
        time = None
        if dep and eta and n > 1:
            time = (dep + (eta - dep) * i / (n - 1)).strftime("%m-%d %H:%M")
        result.append({"location": p.get("name"), "time": time, "status": status})
    return result


@router.get("/transport/{transport_id}")
def get_transport_detail(transport_id: str, db: Session = Depends(get_db)):
    """获取运输详情"""
    t = _get_or_404(db, Transport, transport_id, "运输记录")
    vehicle = db.query(Vehicle).filter(Vehicle.plate == t.vehicle_no).first()
    sensor = db.query(TemperatureSensor).filter(TemperatureSensor.name == f"冷藏车 {t.vehicle_no}").first()
    history = []
    if sensor:
        readings = (db.query(TemperatureReading).filter(TemperatureReading.sensor_id == sensor.id)
                    .order_by(TemperatureReading.recorded_at).all())
        history = [{"time": r.recorded_at.strftime("%H:%M"), "temp": r.temperature} for r in readings]
    data = _transport_dict(t)
    data.update({
        "driver_phone": vehicle.phone if vehicle else None,
        "route_points": _route_points(t),
        "temperature_history": history,
    })
    return data


# ========== 仓库 ==========

def _warehouse_key(warehouse_id: str) -> str:
    # warehouses.id 为字符串主键（与 Supabase 生产库一致），不能转 int：Postgres 不允许 varchar = integer
    return warehouse_id


@router.get("/warehouse")
def get_warehouses(db: Session = Depends(get_db)):
    """获取仓储列表"""
    result = []
    for w in db.query(Warehouse).order_by(Warehouse.created_at, Warehouse.id).all():
        capacity, used = w.capacity or 0, w.used or 0
        result.append({
            "id": w.id,
            "name": w.name,
            "address": w.address,
            "lat": w.lat,
            "lng": w.lng,
            "capacity": w.capacity,
            "used": w.used,
            "available": capacity - used if capacity else 0,
            "utilization": round(used / capacity * 100, 1) if capacity else 0,
            "temperature": w.temperature,
            "humidity": w.humidity,
            "status": w.status,
            "created_at": _fmt(w.created_at, seconds=True),
        })
    return result


@router.get("/warehouse/{warehouse_id}")
def get_warehouse_detail(warehouse_id: str, db: Session = Depends(get_db)):
    """获取仓储详情（温区与在库商品来自数据库）"""
    w = db.query(Warehouse).filter(Warehouse.id == _warehouse_key(warehouse_id)).first()
    if w is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    zones = db.query(StorageZone).filter(StorageZone.warehouse == w.name).order_by(StorageZone.id).all()
    zone_names = {z.id: z.name for z in zones}
    items = []
    if zones:
        items = (db.query(InboundOrderItem).join(InboundOrder)
                 .filter(InboundOrderItem.zone_id.in_(list(zone_names)))
                 .order_by(InboundOrderItem.id).all())
    capacity, used = w.capacity or 0, w.used or 0
    return {
        "id": w.id,
        "name": w.name,
        "address": w.address,
        "capacity": w.capacity,
        "used": w.used,
        "available": capacity - used,
        "temperature": w.temperature,
        "humidity": w.humidity,
        "zones": [{"id": z.id, "name": z.name, "type": z.type,
                   "temp_range": f"{z.temperature_min:g}~{z.temperature_max:g}",
                   "capacity": z.capacity, "used": z.used, "status": z.status} for z in zones],
        "products": [{"name": i.name, "sku": i.sku, "quantity": i.qualified_qty, "zone": zone_names[i.zone_id],
                      "location": i.location, "shelf_date": i.order.inbound_date} for i in items],
    }


class WarehouseIn(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    capacity: Optional[float] = Field(None, ge=0)
    area: Optional[float] = Field(None, ge=0)
    temperature: Optional[float] = Field(None, ge=-60, le=40)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    inventory: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=20)
    manager: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    lat: Optional[float] = None
    lng: Optional[float] = None


class WarehouseCreate(WarehouseIn):
    name: str = Field(..., min_length=1, max_length=100)


def _warehouse_list_dict(w: Warehouse) -> dict:
    return {
        "id": w.id,
        "name": w.name,
        "address": w.address,
        "capacity": w.capacity,
        "area": w.area,
        "temperature": w.temperature,
        "humidity": w.humidity,
        "inventory": w.inventory,
        "status": w.status,
        "manager": w.manager,
        "phone": w.phone,
        "created_at": _fmt(w.created_at, seconds=True),
        "updated_at": _fmt(w.updated_at, seconds=True),
    }


@router.get("/warehouses/list")
def get_warehouses_list(db: Session = Depends(get_db)):
    """获取仓库列表"""
    return [_warehouse_list_dict(w) for w in db.query(Warehouse).order_by(Warehouse.created_at.desc(), Warehouse.id.desc()).all()]


@router.post("/warehouses")
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db)):
    """创建仓库"""
    values = data.model_dump(exclude_none=True)
    values.setdefault("inventory", 0)
    values.setdefault("status", "正常")
    w = Warehouse(**values)
    db.add(w)
    db.commit()
    return {"success": True, "id": w.id, "message": "仓库创建成功"}


def _get_warehouse(db: Session, warehouse_id: str) -> Warehouse:
    w = db.query(Warehouse).filter(Warehouse.id == _warehouse_key(warehouse_id)).first()
    if w is None:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return w


@router.put("/warehouses/{warehouse_id}")
def update_warehouse(warehouse_id: str, data: WarehouseIn, db: Session = Depends(get_db)):
    """更新仓库（只更新提交的字段）"""
    w = _get_warehouse(db, warehouse_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "name" and not value:
            continue
        setattr(w, key, value)
    w.updated_at = datetime.now()
    db.commit()
    return {"success": True, "message": "仓库更新成功"}


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: str, db: Session = Depends(get_db)):
    """删除仓库"""
    db.delete(_get_warehouse(db, warehouse_id))
    db.commit()
    return {"success": True, "message": "仓库删除成功"}


# ========== 温度监控（IoT） ==========

@router.get("/monitoring/temperature")
def get_temperature_monitoring(db: Session = Depends(get_db)):
    """获取各传感器当前温度（最新读数）及区间极值"""
    readings = defaultdict(list)
    for r in db.query(TemperatureReading).order_by(TemperatureReading.recorded_at, TemperatureReading.id):
        readings[r.sensor_id].append(r)
    data = []
    for s in db.query(TemperatureSensor).order_by(TemperatureSensor.id).all():
        rows = readings.get(s.id, [])
        latest = rows[-1] if rows else None
        temps = [r.temperature for r in rows]
        if latest is None:
            status = "离线"
        else:
            status = "正常" if abs(latest.temperature - s.target_temp) <= s.tolerance else "告警"
        data.append({
            "id": s.id,
            "sensor_id": s.id,
            "location": s.name,
            "address": s.location,
            "kind": s.kind,
            "current_temp": latest.temperature if latest else None,
            "target_temp": s.target_temp,
            "min_temp": min(temps) if temps else None,
            "max_temp": max(temps) if temps else None,
            "humidity": latest.humidity if latest else None,
            "status": status,
            "last_update": latest.recorded_at.isoformat() if latest else None,
        })
    return data


class ReadingIn(BaseModel):
    sensor_id: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=-60, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    recorded_at: Optional[datetime] = None


@router.post("/monitoring/readings")
def create_reading(data: ReadingIn, db: Session = Depends(get_db)):
    """IoT 设备上报温湿度读数；超出允许偏差时自动生成温度告警"""
    sensor = _get_or_404(db, TemperatureSensor, data.sensor_id, "传感器")
    reading = TemperatureReading(sensor_id=sensor.id, temperature=data.temperature, humidity=data.humidity,
                                 recorded_at=data.recorded_at or datetime.now())
    db.add(reading)
    deviation = abs(data.temperature - sensor.target_temp)
    alert_id = None
    if deviation > sensor.tolerance:
        severity = "critical" if deviation > 2 * sensor.tolerance else "warning"
        upper = data.temperature > sensor.target_temp
        alert_id = _next_id(db, TemperatureAlert, "A", 4)
        db.add(TemperatureAlert(
            id=alert_id, sensor_id=sensor.id, location=sensor.name, type="温度异常",
            temperature=data.temperature,
            threshold=sensor.target_temp + sensor.tolerance if upper else sensor.target_temp - sensor.tolerance,
            severity=severity, status="未处理",
            message="温度超过阈值" if severity == "warning" else "温度严重超标",
            timestamp=reading.recorded_at))
    db.commit()
    return {"success": True, "id": reading.id, "status": "告警" if alert_id else "正常", "alert_id": alert_id}


@router.get("/monitoring/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """获取温度告警列表"""
    rows = db.query(TemperatureAlert).order_by(TemperatureAlert.timestamp.desc(), TemperatureAlert.id).all()
    return [{
        "id": a.id,
        "sensor_id": a.sensor_id,
        "location": a.location,
        "type": a.type,
        "temperature": a.temperature,
        "threshold": a.threshold,
        "severity": a.severity,
        "status": a.status,
        "message": a.message,
        "timestamp": a.timestamp.isoformat() if a.timestamp else None,
    } for a in rows]


# ========== 质量追溯 ==========

@router.get("/traceability")
def get_traceability(db: Session = Depends(get_db)):
    """获取质量追溯数据（关联同批次品控检查记录）"""
    records = db.query(TraceabilityRecord).order_by(TraceabilityRecord.id.desc()).all()
    batches = [r.product_batch for r in records if r.product_batch]
    inspections = {}
    if batches:
        for q in (db.query(QualityInspection).filter(QualityInspection.batch_no.in_(batches))
                  .order_by(QualityInspection.created_at)):
            inspections[q.batch_no] = q  # 取同批次最新一次检查
    result = []
    for row in records:
        q = inspections.get(row.product_batch)
        result.append({
            "batch_no": row.product_batch,
            "product": row.product_name,
            "source": row.origin_farm,
            "production_date": row.harvest_date or row.planting_date,
            "harvest_time": row.harvest_date,
            "warehouse_in": row.processing_date,
            "warehouse_out": row.sale_date,
            "transport_id": row.logistics_no,
            "retailer": row.retail_outlet,
            "status": row.status,
            "quality_check": {
                "passed": q.result == "合格" if q else row.inspection_report is not None,
                "temperature": q.temperature if q else None,
                "humidity": q.humidity if q else None,
                "inspector": q.inspector if q else None,
                "result": q.result if q else ("合格" if row.inspection_report else "待检"),
            },
        })
    return result


@router.get("/traceability/{batch_no}")
def get_batch_detail(batch_no: str, db: Session = Depends(get_db)):
    """获取批次追溯详情"""
    row = db.query(TraceabilityRecord).filter(TraceabilityRecord.product_batch == batch_no).first()
    if row is None:
        raise HTTPException(status_code=404, detail="批次不存在")

    def at(day, hm):
        return f"{day} {hm}" if day else "无"

    return {
        "batch_no": row.product_batch,
        "product": row.product_name,
        "source": row.origin_farm,
        "production_date": row.harvest_date or row.planting_date,
        "origin_address": row.origin_address,
        "planting_date": row.planting_date,
        "harvest_date": row.harvest_date,
        "processing_date": row.processing_date,
        "processing_factory": row.processing_factory,
        "logistics_company": row.logistics_company,
        "logistics_no": row.logistics_no,
        "warehouse": row.warehouse,
        "retail_outlet": row.retail_outlet,
        "sale_date": row.sale_date,
        "certifications": row.certifications,
        "inspection_report": row.inspection_report,
        "trace_code": row.trace_code,
        "status": row.status,
        "trace_data": [
            {"stage": "种植", "location": row.origin_address, "time": at(row.planting_date, "08:00"), "detail": "播种/定植", "operator": "基地管理员"},
            {"stage": "采收", "location": row.origin_farm, "time": at(row.harvest_date, "06:00"), "detail": "采收完成", "operator": "采收工人"},
            {"stage": "加工", "location": row.processing_factory or "无", "time": at(row.processing_date, "10:00"), "detail": "加工包装", "operator": "加工人员"},
            {"stage": "入库", "location": row.warehouse or "无", "time": at(row.processing_date, "18:00"), "detail": "入库存储", "operator": "仓管人员"},
            {"stage": "出库", "location": row.warehouse or "无", "time": at(row.sale_date, "08:00"), "detail": "装车运输", "operator": "物流司机"},
            {"stage": "配送", "location": row.retail_outlet or "无", "time": at(row.sale_date, "14:00"), "detail": "已送达门店", "operator": "配送员"},
        ],
    }


# ========== 数据分析 ==========

def _compliance(db: Session, kind: Optional[str] = None) -> float:
    """温度读数落在目标温度允许偏差内的比例（%）"""
    q = db.query(TemperatureReading, TemperatureSensor).join(
        TemperatureSensor, TemperatureReading.sensor_id == TemperatureSensor.id)
    if kind:
        q = q.filter(TemperatureSensor.kind == kind)
    rows = q.all()
    ok = sum(1 for r, s in rows if abs(r.temperature - s.target_temp) <= s.tolerance)
    return _pct(ok, len(rows))


@router.get("/analytics")
def get_cold_chain_analytics(db: Session = Depends(get_db)):
    """获取冷链分析数据（全部由数据库记录计算）"""
    now = datetime.now()
    vehicles = db.query(Vehicle).all()
    transports = db.query(Transport).all()
    # 准点：已到达，或仍在途/待发但尚未超过预计到达时间
    on_time = sum(1 for t in transports
                  if t.status == "arrived" or (isinstance(t.eta, datetime) and t.eta >= now))
    warehouses = db.query(Warehouse).all()
    total_capacity = sum(w.capacity or 0 for w in warehouses)
    total_used = sum(w.used or 0 for w in warehouses)
    inspections = db.query(QualityInspection).all()
    failed = [q for q in inspections if q.result == "不合格"]
    latest_month = db.query(OperatingCost.month).order_by(OperatingCost.month.desc()).first()
    costs = {"electricity": 0.0, "fuel": 0.0, "maintenance": 0.0}
    if latest_month:
        for c in db.query(OperatingCost).filter(OperatingCost.month == latest_month[0]):
            costs[c.category] = round(costs.get(c.category, 0) + c.amount, 2)
    return {
        "transport": {
            "total_vehicles": len(vehicles),
            "active": sum(1 for v in vehicles if v.status == "运输中"),
            "on_time_rate": _pct(on_time, len(transports)),
            "avg_temp_compliance": _compliance(db, "冷藏车"),
        },
        "warehouse": {
            "total_capacity": total_capacity,
            "utilization": _pct(total_used, total_capacity),
            "avg_temp_stability": _compliance(db, "冷库"),
        },
        "quality": {
            "total_batches": len({q.batch_no for q in inspections}),
            "pass_rate": _pct(sum(1 for q in inspections if q.result == "合格"), len(inspections)),
            # 不合格检查即计为质量投诉；其中货损类（温度超标 / 包装损坏）需要理赔
            "complaints": len(failed),
            "claims": sum(1 for q in failed if q.remark in ("温度超标", "包装损坏")),
        },
        "cost": {**costs, "month": latest_month[0] if latest_month else None},
    }


# ========== 品控管理 ==========

INSPECTION_TYPES = ("入库检查", "出库检查", "在库检查", "运输检查", "终端检查")


def _inspection_dict(q: QualityInspection, detail: bool = False) -> dict:
    data = {
        "id": q.id,
        "type": q.type,
        "product": q.product,
        "batch_no": q.batch_no,
        "quantity": q.quantity,
        "result": q.result,
        "score": q.score,
        "temperature": q.temperature,
        "humidity": q.humidity,
        "pesticide_residue": q.pesticide_residue,
        "heavy_metal": q.heavy_metal,
        "inspector": q.inspector,
        "location": q.location,
        "remark": q.remark,
        "created_at": _fmt(q.created_at),
    }
    if detail:
        data["items"] = q.items or []
        data["images"] = []
    return data


@router.get("/quality/inspections")
def get_quality_inspections(db: Session = Depends(get_db)):
    """获取品控检查记录列表"""
    rows = db.query(QualityInspection).order_by(QualityInspection.created_at.desc(), QualityInspection.id.desc())
    return [_inspection_dict(q) for q in rows]


@router.get("/quality/inspections/{inspection_id}")
def get_quality_inspection_detail(inspection_id: str, db: Session = Depends(get_db)):
    """获取品控检查详情"""
    return _inspection_dict(_get_or_404(db, QualityInspection, inspection_id, "品控检查记录"), detail=True)


class InspectionItem(BaseModel):
    name: str = Field(..., min_length=1)
    result: Literal["合格", "待复检", "不合格"]
    score: float = Field(..., ge=0, le=100)


class InspectionCreate(BaseModel):
    type: Literal["入库检查", "出库检查", "在库检查", "运输检查", "终端检查"]
    product: str = Field(..., min_length=1, max_length=100)
    batch_no: str = Field(..., min_length=1, max_length=50)
    quantity: float = Field(..., gt=0)
    result: Literal["合格", "待复检", "不合格"]
    score: float = Field(..., ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=-60, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    pesticide_residue: Optional[float] = Field(None, ge=0)
    heavy_metal: Optional[float] = Field(None, ge=0)
    inspector: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = Field(None, max_length=200)
    items: List[InspectionItem] = []


@router.post("/quality/inspections")
def create_quality_inspection(data: InspectionCreate, db: Session = Depends(get_db)):
    """创建品控检查记录"""
    q = QualityInspection(id=_next_id(db, QualityInspection, "QC", 5), created_at=datetime.now(), **data.model_dump())
    db.add(q)
    db.commit()
    return {"success": True, "id": q.id, "message": "品控检查记录创建成功"}


@router.get("/quality/standards")
def get_quality_standards():
    """获取品控标准（行业参考标准，静态配置）"""
    return {
        "standards": [
            {"id": "QS001", "name": "新鲜蔬菜品控标准", "category": "蔬菜",
             "temperature": {"min": 0, "max": 8, "unit": "°C"}, "humidity": {"min": 85, "max": 95, "unit": "%"},
             "pesticide_residue_max": 0.5, "heavy_metal_max": 0.1, "shelf_days": 7},
            {"id": "QS002", "name": "水果品控标准", "category": "水果",
             "temperature": {"min": 0, "max": 12, "unit": "°C"}, "humidity": {"min": 80, "max": 90, "unit": "%"},
             "pesticide_residue_max": 0.3, "heavy_metal_max": 0.05, "shelf_days": 14},
            {"id": "QS003", "name": "冷冻食品品控标准", "category": "冷冻食品",
             "temperature": {"min": -25, "max": -18, "unit": "°C"}, "humidity": {"min": 70, "max": 85, "unit": "%"},
             "pesticide_residue_max": 0.1, "heavy_metal_max": 0.02, "shelf_days": 180},
            {"id": "QS004", "name": "肉类品控标准", "category": "肉类",
             "temperature": {"min": -2, "max": 4, "unit": "°C"}, "humidity": {"min": 75, "max": 85, "unit": "%"},
             "pesticide_residue_max": 0.2, "heavy_metal_max": 0.05, "shelf_days": 5},
        ]
    }


# ========== 库存预警 ==========

ALERT_TYPES = ("库存不足", "库存过多", "临期预警", "温度异常", "湿度异常")
_ALERT_SUGGESTIONS = {
    "库存不足": ["建议立即补货", "检查供应链是否有延迟", "考虑提高安全库存量"],
    "库存过多": ["暂停该商品入库预约", "安排促销或调拨至其他仓库"],
    "临期预警": ["优先安排出库（先进先出）", "联系货主确认处理方式"],
    "温度异常": ["检查制冷设备运行状态", "必要时将货物转移至备用温区"],
    "湿度异常": ["检查除湿/加湿设备", "检查库门密封情况"],
}


def get_alert_message(alert_type: str, current: float) -> str:
    """生成预警消息"""
    messages = {
        "库存不足": f"当前库存{current:.0f}件，低于安全库存",
        "库存过多": f"当前库存{current:.0f}件，超过最大库存",
        "临期预警": f"还有{int(current)}天到期，请及时处理",
        "温度异常": f"当前温度{current:g}°C，超出正常范围",
        "湿度异常": f"当前湿度{current:g}%，超出正常范围",
    }
    return messages.get(alert_type, "")


def _alert_dict(a: InventoryAlert) -> dict:
    return {
        "id": a.id,
        "type": a.type,
        "level": a.level,
        "product": a.product,
        "warehouse": a.warehouse,
        "current_value": a.current_value,
        "threshold": a.threshold,
        "unit": a.unit,
        "status": a.status,
        "message": get_alert_message(a.type, a.current_value),
        "created_at": _fmt(a.created_at),
    }


@router.get("/inventory/alerts")
def get_inventory_alerts(db: Session = Depends(get_db)):
    """获取库存预警列表（按级别、时间排序）"""
    rows = db.query(InventoryAlert).all()
    rows.sort(key=lambda a: (LEVEL_ORDER.get(a.level, 4), -a.created_at.timestamp(), a.id))
    return [_alert_dict(a) for a in rows]


@router.get("/inventory/alerts/{alert_id}")
def get_inventory_alert_detail(alert_id: str, db: Session = Depends(get_db)):
    """获取库存预警详情"""
    a = _get_or_404(db, InventoryAlert, alert_id, "预警")
    data = _alert_dict(a)
    data.update({
        "product_code": a.product_code,
        "zone": a.zone,
        "current_stock": a.current_value if a.type in ("库存不足", "库存过多") else None,
        "min_stock": a.threshold if a.type == "库存不足" else None,
        "max_stock": a.threshold if a.type == "库存过多" else None,
        "history": [],
        "suggestions": _ALERT_SUGGESTIONS.get(a.type, []),
        "resolve_remark": a.resolve_remark,
        "updated_at": _fmt(a.resolved_at or a.created_at, seconds=True),
    })
    return data


class ResolveIn(BaseModel):
    remark: Optional[str] = Field(None, max_length=200)


@router.post("/inventory/alerts/{alert_id}/resolve")
def resolve_inventory_alert(alert_id: str, data: Optional[ResolveIn] = None, db: Session = Depends(get_db)):
    """处理库存预警"""
    a = _get_or_404(db, InventoryAlert, alert_id, "预警")
    if a.status == "已解决":
        raise HTTPException(status_code=409, detail="预警已处理")
    a.status = "已解决"
    a.resolved_at = datetime.now()
    a.resolve_remark = data.remark if data else None
    db.commit()
    return {"success": True, "message": f"预警 {alert_id} 已标记为已处理"}


def _rule_dict(r: InventoryRule) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "type": r.type,
        "enabled": bool(r.enabled),
        "threshold": r.threshold,
        "unit": r.unit,
        "product_categories": r.product_categories or [],
        "notify_channels": r.notify_channels or [],
    }


@router.get("/inventory/rules")
def get_inventory_rules(db: Session = Depends(get_db)):
    """获取库存预警规则"""
    return {"rules": [_rule_dict(r) for r in db.query(InventoryRule).order_by(InventoryRule.id)]}


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: Literal["库存不足", "库存过多", "临期预警", "温度异常", "湿度异常"]
    threshold: float
    unit: str = Field(..., min_length=1, max_length=10)
    enabled: bool = True
    product_categories: List[str] = ["全部"]
    notify_channels: List[str] = Field(default_factory=lambda: ["APP"], min_length=1)


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    threshold: Optional[float] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=10)
    enabled: Optional[bool] = None
    product_categories: Optional[List[str]] = None
    notify_channels: Optional[List[str]] = Field(None, min_length=1)


@router.post("/inventory/rules")
def create_inventory_rule(data: RuleCreate, db: Session = Depends(get_db)):
    """创建库存预警规则"""
    rule = InventoryRule(id=_next_id(db, InventoryRule, "RULE", 3), **data.model_dump())
    db.add(rule)
    db.commit()
    return {"success": True, "id": rule.id, "message": "预警规则创建成功"}


@router.put("/inventory/rules/{rule_id}")
def update_inventory_rule(rule_id: str, data: RuleUpdate, db: Session = Depends(get_db)):
    """更新预警规则（如启用/停用）"""
    rule = _get_or_404(db, InventoryRule, rule_id, "预警规则")
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(rule, key, value)
    db.commit()
    return {"success": True, "rule": _rule_dict(rule)}


@router.get("/inventory/stats")
def get_inventory_stats(db: Session = Depends(get_db)):
    """获取库存统计概览（由温区、入库明细与预警记录计算）"""
    alerts = db.query(InventoryAlert).all()
    open_alerts = [a for a in alerts if a.status != "已解决"]
    now = datetime.now()
    week_start = now - timedelta(days=7)
    this_week = [a for a in alerts if a.created_at >= week_start]
    skus = {sku for (sku,) in db.query(InboundOrderItem.sku).distinct()}
    total_pallets = sum(z.used or 0 for z in db.query(StorageZone).all())

    def count_open(t):
        return sum(1 for a in open_alerts if a.type == t)

    week_resolved = sum(1 for a in this_week if a.status == "已解决")
    return {
        "total_products": len(skus),
        "total_stock": total_pallets * UNITS_PER_PALLET,
        "low_stock_count": count_open("库存不足"),
        "overstock_count": count_open("库存过多"),
        "expiring_soon_count": count_open("临期预警"),
        "temp_alert_count": count_open("温度异常"),
        "today_resolved": sum(1 for a in alerts if a.resolved_at and a.resolved_at.date() == now.date()),
        "this_week": {
            "total_alerts": len(this_week),
            "resolved": week_resolved,
            "pending": len(this_week) - week_resolved,
        },
    }


# ========== 货主管理 ==========

def _owner_zone_stats(db: Session) -> dict:
    stats = defaultdict(lambda: {"warehouses": set(), "zones": 0, "pallets": 0})
    for z in db.query(StorageZone).filter(StorageZone.owner_code.isnot(None)):
        s = stats[z.owner_code]
        s["warehouses"].add(z.warehouse)
        s["zones"] += 1
        s["pallets"] += z.used or 0
    return stats


@router.get("/owner/list")
def get_owner_list(db: Session = Depends(get_db)):
    """获取货主列表（仓库数/温区数/库存量由其租用的温区计算）"""
    stats = _owner_zone_stats(db)
    result = []
    for o in db.query(CargoOwner).order_by(CargoOwner.id.desc()).all():
        s = stats.get(o.code, {"warehouses": set(), "zones": 0, "pallets": 0})
        result.append({
            "id": o.id,
            "code": o.code,
            "name": o.name,
            "contact": o.contact,
            "phone": o.phone,
            "email": o.email,
            "address": o.address,
            "status": o.status,
            "created_at": _fmt(o.created_at, seconds=True),
            "warehouse_count": len(s["warehouses"]),
            "zone_count": s["zones"],
            "total_stock": s["pallets"] * UNITS_PER_PALLET,
        })
    return result


@router.get("/owner/{owner_id}")
def get_owner_detail(owner_id: int, db: Session = Depends(get_db)):
    """获取货主详情"""
    o = _get_or_404(db, CargoOwner, owner_id, "货主")
    by_wh = defaultdict(int)
    for z in db.query(StorageZone).filter(StorageZone.owner_code == o.code):
        by_wh[z.warehouse] += 1
    wh_ids = {w.name: w.id for w in db.query(Warehouse).filter(Warehouse.name.in_(list(by_wh)))} if by_wh else {}
    return {
        "id": o.id,
        "code": o.code,
        "name": o.name,
        "contact": o.contact,
        "phone": o.phone,
        "email": o.email,
        "address": o.address,
        "status": o.status,
        "warehouses": [{"id": wh_ids.get(name), "name": name, "zones": n} for name, n in sorted(by_wh.items())],
        "pricing_model": None,
        "contracts": [],
    }


class OwnerIn(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    contact: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=200)
    status: Optional[Literal["正常", "暂停"]] = None


class OwnerCreate(OwnerIn):
    name: str = Field(..., min_length=1, max_length=100)


@router.post("/owner")
def create_owner(data: OwnerCreate, db: Session = Depends(get_db)):
    """创建货主"""
    max_id = db.query(CargoOwner.id).order_by(CargoOwner.id.desc()).first()
    code = f"OW{1000 + (max_id[0] if max_id else 0) + 1}"
    values = data.model_dump(exclude_none=True)
    values.setdefault("status", "正常")
    owner = CargoOwner(code=code, **values)
    db.add(owner)
    db.commit()
    return {"success": True, "id": owner.id, "code": code}


@router.put("/owner/{owner_id}")
def update_owner(owner_id: int, data: OwnerIn, db: Session = Depends(get_db)):
    """更新货主信息（只更新提交的字段）"""
    owner = _get_or_404(db, CargoOwner, owner_id, "货主")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key in ("name", "status") and value is None:
            continue
        setattr(owner, key, value)
    db.commit()
    return {"success": True, "message": f"货主 {owner_id} 更新成功"}


@router.delete("/owner/{owner_id}")
def delete_owner(owner_id: int, db: Session = Depends(get_db)):
    """删除货主"""
    db.delete(_get_or_404(db, CargoOwner, owner_id, "货主"))
    db.commit()
    return {"success": True, "message": f"货主 {owner_id} 删除成功"}


# ========== 温区管理 ==========

@router.get("/zone/list")
def get_zone_list(db: Session = Depends(get_db)):
    """获取温区列表"""
    return [{
        "id": z.id,
        "code": z.code,
        "name": z.name,
        "type": z.type,
        "temperature_min": z.temperature_min,
        "temperature_max": z.temperature_max,
        "warehouse": z.warehouse,
        "owner_code": z.owner_code,
        "capacity": z.capacity,
        "used": z.used,
        "available": z.capacity - (z.used or 0),
        "distance_to_pick": z.distance_to_pick,
        "status": z.status,
    } for z in db.query(StorageZone).order_by(StorageZone.id).all()]


# ========== 入库预约 ==========

def _appointment_dict(a: InboundAppointment, detail: bool = False) -> dict:
    items = a.items or []
    data = {
        "id": a.id,
        "owner": a.owner,
        "owner_code": a.owner_code,
        "vehicle_no": a.vehicle_no,
        "driver": a.driver,
        "driver_phone": a.driver_phone,
        "estimated_arrival": _fmt(a.estimated_arrival),
        "actual_arrival": _fmt(a.actual_arrival),
        "appointment_date": a.estimated_arrival.strftime("%Y-%m-%d") if a.estimated_arrival else None,
        "expected_items": len(items),
        "expected_quantity": sum(i["quantity"] for i in items),
        "status": a.status,
        "dock": a.dock,
        "zone": a.zone,
        "cargo_type": a.cargo_type,
        "remark": a.remark or "",
    }
    if detail:
        data["items"] = items
    return data


@router.get("/inbound/appointments")
def get_inbound_appointments(db: Session = Depends(get_db)):
    """获取入库预约列表"""
    rows = db.query(InboundAppointment).order_by(InboundAppointment.estimated_arrival.desc(),
                                                 InboundAppointment.id.desc())
    return [_appointment_dict(a) for a in rows]


@router.get("/inbound/appointments/{appointment_id}")
def get_appointment_detail(appointment_id: str, db: Session = Depends(get_db)):
    """获取预约详情"""
    return _appointment_dict(_get_or_404(db, InboundAppointment, appointment_id, "预约"), detail=True)


class AppointmentItem(BaseModel):
    sku: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    unit: str = "件"
    barcode: Optional[str] = Field(None, max_length=30)
    storage_type: Literal["冷藏", "冷冻", "常温"] = "冷藏"


class AppointmentCreate(BaseModel):
    owner_code: Optional[str] = Field(None, max_length=20)
    owner: Optional[str] = Field(None, min_length=1, max_length=100)
    vehicle_no: str = Field(..., min_length=1, max_length=20)
    driver: Optional[str] = Field(None, max_length=50)
    driver_phone: Optional[str] = Field(None, max_length=20)
    estimated_arrival: datetime
    dock: Optional[str] = Field(None, max_length=10)
    zone: Optional[str] = Field(None, max_length=50)
    cargo_type: Optional[str] = Field(None, max_length=50)
    remark: Optional[str] = Field(None, max_length=200)
    items: List[AppointmentItem] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _owner_given(self):
        if not self.owner_code and not self.owner:
            raise ValueError("owner_code 与 owner 至少提供一个")
        return self


@router.post("/inbound/appointments")
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    """创建入库预约"""
    owner_name = data.owner
    if data.owner_code:
        owner = db.query(CargoOwner).filter(CargoOwner.code == data.owner_code).first()
        if owner is None:
            raise HTTPException(status_code=404, detail="货主不存在")
        owner_name = owner.name
    appt = InboundAppointment(
        id=_next_id(db, InboundAppointment, f"INB{datetime.now():%Y%m}", 4),
        owner=owner_name, owner_code=data.owner_code, vehicle_no=data.vehicle_no, driver=data.driver,
        driver_phone=data.driver_phone, estimated_arrival=data.estimated_arrival.replace(tzinfo=None),
        dock=data.dock, zone=data.zone, cargo_type=data.cargo_type, remark=data.remark,
        items=[i.model_dump() for i in data.items], status="待签到", created_at=datetime.now())
    db.add(appt)
    db.commit()
    return {"success": True, "id": appt.id}


@router.put("/inbound/appointments/{appointment_id}/checkin")
def checkin_appointment(appointment_id: str, db: Session = Depends(get_db)):
    """签到确认到货：待签到 -> 已签到"""
    appt = _get_or_404(db, InboundAppointment, appointment_id, "预约")
    if appt.status != "待签到":
        raise HTTPException(status_code=409, detail=f"当前状态为{appt.status}，不能签到")
    appt.status = "已签到"
    appt.actual_arrival = datetime.now()
    db.commit()
    return {"success": True, "message": f"预约 {appointment_id} 已签到", "status": appt.status}


@router.put("/inbound/appointments/{appointment_id}/receive")
def start_receive(appointment_id: str, db: Session = Depends(get_db)):
    """开始收货：已签到 -> 收货中，并按预约货物生成入库单"""
    appt = _get_or_404(db, InboundAppointment, appointment_id, "预约")
    if appt.status != "已签到":
        raise HTTPException(status_code=409, detail=f"当前状态为{appt.status}，不能开始收货")
    zone = db.query(StorageZone).filter(StorageZone.name == appt.zone).first() if appt.zone else None
    now = datetime.now()
    order = InboundOrder(
        id=_next_id(db, InboundOrder, f"IOR{now:%Y%m}", 4), appointment_id=appt.id, owner=appt.owner,
        warehouse=zone.warehouse if zone else None, inbound_date=now.strftime("%Y-%m-%d"), status="待收货",
        dock=appt.dock, created_at=now)
    for i in appt.items or []:
        order.items.append(InboundOrderItem(
            sku=i["sku"], name=i["name"], barcode=i.get("barcode"), storage_type=i.get("storage_type", "冷藏"),
            expected_qty=i["quantity"], received_qty=0, qualified_qty=0))
    appt.status = "收货中"
    db.add(order)
    db.commit()
    return {"success": True, "status": appt.status, "order_id": order.id}


# ========== 入库单 ==========

def _item_status(i: InboundOrderItem) -> str:
    if not i.received_qty:
        return "待收货"
    return "已完成" if i.received_qty >= i.expected_qty else "部分收货"


def _item_dict(i: InboundOrderItem) -> dict:
    received, qualified = i.received_qty or 0, i.qualified_qty or 0
    return {
        "id": i.id,
        "sku": i.sku,
        "name": i.name,
        "barcode": i.barcode,
        "storage_type": i.storage_type,
        "expected_qty": i.expected_qty,
        "received_qty": received,
        "qualified_qty": qualified,
        "status": _item_status(i),
        "zone_id": i.zone_id,
        "location": i.location,
        # 兼容旧字段
        "expected": i.expected_qty,
        "received": received,
        "qualified": qualified,
        "unqualified": received - qualified,
    }


def _order_dict(o: InboundOrder) -> dict:
    items = o.items
    received = sum(i.received_qty or 0 for i in items)
    qualified = sum(i.qualified_qty or 0 for i in items)
    return {
        "id": o.id,
        "appointment_id": o.appointment_id,
        "owner": o.owner,
        "warehouse": o.warehouse,
        "inbound_date": o.inbound_date,
        "status": o.status,
        "total_items": len(items),
        "total_quantity": sum(i.expected_qty for i in items),
        "received_quantity": received,
        "qualified_quantity": qualified,
        "unqualified_quantity": received - qualified,
        "dock": o.dock,
        "receiver": o.receiver,
        "created_at": _fmt(o.created_at),
        "items": [_item_dict(i) for i in items],
    }


@router.get("/inbound/orders")
def get_inbound_orders(db: Session = Depends(get_db)):
    """获取入库单列表（含货物明细）"""
    rows = db.query(InboundOrder).order_by(InboundOrder.created_at.desc(), InboundOrder.id.desc()).all()
    return [_order_dict(o) for o in rows]


@router.get("/inbound/orders/{order_id}")
def get_inbound_order_detail(order_id: str, db: Session = Depends(get_db)):
    """获取入库单详情"""
    o = _get_or_404(db, InboundOrder, order_id, "入库单")
    data = _order_dict(o)
    received, qualified = data["received_quantity"], data["qualified_quantity"]
    data["quality_check"] = {
        "status": "已完成" if o.status == "已质检" else "未完成",
        "passed": received > 0 and received == qualified,
        "qualified_rate": round(qualified / received, 4) if received else None,
    }
    return data


class ReceiveIn(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    qualified_qty: int = Field(..., ge=0)
    remark: Optional[str] = Field(None, max_length=200)

    @model_validator(mode="after")
    def _qualified_le_quantity(self):
        if self.qualified_qty > self.quantity:
            raise ValueError("合格数量不能大于收货数量")
        return self


@router.post("/inbound/orders/{order_id}/receive")
def receive_goods(order_id: str, data: ReceiveIn, db: Session = Depends(get_db)):
    """收货登记：累加 SKU 的已收/合格数量，全部收齐后入库单变为已入库"""
    order = _get_or_404(db, InboundOrder, order_id, "入库单")
    if order.status not in ("待收货", "收货中"):
        raise HTTPException(status_code=409, detail=f"入库单状态为{order.status}，不能收货")
    item = next((i for i in order.items if i.sku == data.sku), None)
    if item is None:
        raise HTTPException(status_code=404, detail="入库单中不存在该 SKU")
    remaining = item.expected_qty - (item.received_qty or 0)
    if data.quantity > remaining:
        raise HTTPException(status_code=400, detail=f"收货数量超过待收数量 {remaining}")
    item.received_qty = (item.received_qty or 0) + data.quantity
    item.qualified_qty = (item.qualified_qty or 0) + data.qualified_qty
    if all((i.received_qty or 0) >= i.expected_qty for i in order.items):
        order.status = "已入库"
        if order.appointment_id:
            appt = db.get(InboundAppointment, order.appointment_id)
            if appt:
                appt.status = "已完成"
    else:
        order.status = "收货中"
    db.commit()
    return {"success": True, "order": _order_dict(order)}


# ========== 上架建议 ==========

def _pallets(qty: int) -> int:
    return math.ceil(qty / UNITS_PER_PALLET)


def _slot_location(zone: StorageZone, position: int) -> str:
    """按托位序号生成货位号：{库区字母}{排}-{层}-{位}"""
    p = position - 1
    return f"{zone.code}{p // 60 + 1:02d}-{(p // 20) % 3 + 1:02d}-{p % 20 + 1:02d}"


@router.get("/inbound/suggestions/{order_id}")
def get_putaway_suggestions(order_id: str, db: Session = Depends(get_db)):
    """智能上架建议：按温度匹配、温区剩余容量与距出库口距离打分（确定性计算）"""
    order = _get_or_404(db, InboundOrder, order_id, "入库单")
    zones = db.query(StorageZone).filter(StorageZone.status == "正常").order_by(StorageZone.id).all()
    reserved = defaultdict(int)  # 本次建议已预占的托位，避免多个 SKU 挤进同一个满温区
    suggestions = []
    for item in order.items:
        if item.zone_id:
            continue  # 已上架
        qty = item.qualified_qty if item.received_qty else item.expected_qty
        if not qty:
            continue
        need = _pallets(qty)
        primary, fallback = STORAGE_ZONE_TYPES.get(item.storage_type, (None, None))
        best = None
        for z in zones:
            if z.type == primary:
                temp_match = 1.0
            elif fallback and z.type == fallback:
                temp_match = 0.8
            else:
                continue
            free = z.capacity - (z.used or 0) - reserved[z.id]
            if free < need:
                continue
            balance = (free - need) / z.capacity
            proximity = 1 - min(z.distance_to_pick or 0, 50) / 50
            score = 0.5 * temp_match + 0.3 * balance + 0.2 * proximity
            if order.warehouse and z.warehouse != order.warehouse:
                score -= 0.1  # 跨仓调拨扣分
            key = (round(score, 6), -int(z.id[1:]) if z.id[1:].isdigit() else 0)
            if best is None or key > best[0]:
                best = (key, z, temp_match, balance, score)
        if best is None:
            suggestions.append({"order_id": order.id, "item_id": item.id, "sku": item.sku, "name": item.name,
                                "quantity": qty, "suggested_location": None, "zone": None, "zone_id": None,
                                "reason": "无可用温区", "distance_to_pick": None, "confidence": 0.0})
            continue
        _, z, temp_match, balance, score = best
        position = (z.used or 0) + reserved[z.id] + 1
        reserved[z.id] += need
        reasons = ["温度匹配" if temp_match == 1.0 else "温度兼容"]
        if balance >= 0.5:
            reasons.append("库存均衡")
        if (z.distance_to_pick or 0) <= 10:
            reasons.append("靠近出库口")
        suggestions.append({
            "order_id": order.id,
            "item_id": item.id,
            "sku": item.sku,
            "name": item.name,
            "quantity": qty,
            "suggested_location": _slot_location(z, position),
            "zone": z.name,
            "zone_id": z.id,
            "warehouse": z.warehouse,
            "reason": " + ".join(reasons),
            "distance_to_pick": z.distance_to_pick,
            "confidence": round(max(score, 0), 4),
        })
    return suggestions


class PutawayIn(BaseModel):
    sku: str = Field(..., min_length=1)
    zone_id: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1, max_length=30)


@router.post("/inbound/orders/{order_id}/putaway")
def confirm_putaway(order_id: str, data: PutawayIn, db: Session = Depends(get_db)):
    """确认上架：记录货位并占用温区托位"""
    order = _get_or_404(db, InboundOrder, order_id, "入库单")
    item = next((i for i in order.items if i.sku == data.sku and not i.zone_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="入库单中不存在待上架的该 SKU")
    zone = _get_or_404(db, StorageZone, data.zone_id, "温区")
    if zone.status != "正常":
        raise HTTPException(status_code=409, detail=f"温区{zone.name}{zone.status}，不能上架")
    qty = item.qualified_qty if item.received_qty else item.expected_qty
    need = _pallets(qty)
    if zone.capacity - (zone.used or 0) < need:
        raise HTTPException(status_code=400, detail="温区剩余容量不足")
    item.zone_id, item.location = zone.id, data.location
    zone.used = (zone.used or 0) + need
    db.commit()
    return {"success": True, "message": f"{item.sku} 已上架到 {data.location}"}


# ========== 作业管理 ==========

def _task_dict(t: OperationTask, detail: bool = False) -> dict:
    data = {
        "id": t.id,
        "type": t.type,
        "priority": t.priority,
        "status": t.status,
        "owner": t.owner,
        "location": t.location,
        "quantity": t.quantity,
        "assigned_to": t.assigned_to,
        "assigned_at": _fmt(t.assigned_at),
        "started_at": _fmt(t.started_at),
        "completed_at": _fmt(t.completed_at),
        "barcode": t.barcode,
        "batch_id": t.batch_id,
    }
    if detail:
        data.update({"items": t.items or [], "target_location": t.target_location, "history": t.history or []})
    return data


@router.get("/operation/tasks")
def get_operation_tasks(db: Session = Depends(get_db)):
    """获取作业任务列表"""
    return [_task_dict(t) for t in db.query(OperationTask).order_by(OperationTask.id.desc()).all()]


@router.get("/operation/tasks/{task_id}")
def get_task_detail(task_id: str, db: Session = Depends(get_db)):
    """获取作业任务详情"""
    return _task_dict(_get_or_404(db, OperationTask, task_id, "任务"), detail=True)


class TaskActionIn(BaseModel):
    operator: Optional[str] = Field(None, max_length=50)
    error_count: Optional[int] = Field(None, ge=0)


class ScanIn(BaseModel):
    barcode: str = Field(..., min_length=1, max_length=30)
    operator: Optional[str] = Field(None, max_length=50)


def _log(task: OperationTask, action: str, operator: str, detail: Optional[str] = None):
    entry = {"action": action, "operator": operator, "time": _fmt(datetime.now())}
    if detail:
        entry["detail"] = detail
    task.history = [*(task.history or []), entry]  # 重新赋值以便 JSON 列被标记为已修改


@router.post("/operation/tasks/{task_id}/start")
def start_task(task_id: str, data: Optional[TaskActionIn] = None, db: Session = Depends(get_db)):
    """开始执行任务：待执行 -> 执行中"""
    task = _get_or_404(db, OperationTask, task_id, "任务")
    if task.status != "待执行":
        raise HTTPException(status_code=409, detail=f"任务状态为{task.status}，不能开始")
    task.status = "执行中"
    task.started_at = datetime.now()
    _log(task, "开始执行", (data.operator if data and data.operator else None) or task.assigned_to or "系统")
    db.commit()
    return {"success": True, "message": f"任务 {task_id} 开始执行", "started_at": _fmt(task.started_at)}


@router.post("/operation/tasks/{task_id}/complete")
def complete_task(task_id: str, data: Optional[TaskActionIn] = None, db: Session = Depends(get_db)):
    """完成任务：执行中 -> 已完成"""
    task = _get_or_404(db, OperationTask, task_id, "任务")
    if task.status != "执行中":
        raise HTTPException(status_code=409, detail=f"任务状态为{task.status}，不能完成")
    task.status = "已完成"
    task.completed_at = datetime.now()
    if data and data.error_count is not None:
        task.error_count = data.error_count
    _log(task, "完成任务", (data.operator if data and data.operator else None) or task.assigned_to or "系统")
    db.commit()
    return {"success": True, "message": f"任务 {task_id} 已完成", "completed_at": _fmt(task.completed_at)}


@router.post("/operation/tasks/{task_id}/scan")
def scan_item(task_id: str, data: ScanIn, db: Session = Depends(get_db)):
    """扫描条码（任务条码或任务内商品条码），仅执行中的任务可扫描"""
    task = _get_or_404(db, OperationTask, task_id, "任务")
    if task.status != "执行中":
        raise HTTPException(status_code=409, detail=f"任务状态为{task.status}，不能扫描")
    items = task.items or []
    item = next((i for i in items if i.get("barcode") == data.barcode), None)
    if item is None and data.barcode == task.barcode and items:
        item = items[0]
    if item is None:
        raise HTTPException(status_code=404, detail="条码不属于该任务")
    _log(task, "扫描商品", data.operator or task.assigned_to or "系统", f"{item['sku']} x{item['quantity']}")
    db.commit()
    return {"success": True, "scanned": True, "item": {k: item.get(k) for k in ("sku", "name", "quantity", "location")}}


# ========== 人员绩效 ==========

@router.get("/operation/performance")
def get_operator_performance(db: Session = Depends(get_db)):
    """人员绩效：由作业任务记录统计"""
    tasks_by_person = defaultdict(list)
    for t in db.query(OperationTask).all():
        tasks_by_person[t.assigned_to].append(t)
    today = datetime.now().strftime("%Y-%m-%d")
    result = []
    for op in db.query(Operator).order_by(Operator.employee_id).all():
        tasks = tasks_by_person.get(op.name, [])
        done = [t for t in tasks if t.status == "已完成"]
        minutes = [(t.completed_at - t.started_at).total_seconds() / 60 for t in done
                   if t.completed_at and t.started_at]
        errors = sum(t.error_count or 0 for t in done)
        accuracy = round(sum(1 for t in done if not t.error_count) / len(done), 3) if done else 1.0
        result.append({
            "employee_id": op.employee_id,
            "name": op.name,
            "department": op.department,
            "date": today,
            "tasks_completed": len(done),
            "tasks_handled": len([t for t in tasks if t.status != "已取消"]),
            "error_count": errors,
            "accuracy_rate": accuracy,
            "avg_task_time": round(sum(minutes) / len(minutes), 1) if minutes else 0,
            "working_hours": round(sum(minutes) / 60, 1),
            # 评分 = 准确率 60 分 + 完成量（每单 8 分，封顶 40 分）
            "score": min(100, round(accuracy * 60 + min(len(done), 5) * 8)),
        })
    result.sort(key=lambda r: (-r["score"], r["employee_id"]))
    return result


# ========== 智能批次调度 ==========

TASK_SETUP_MINUTES = 5  # 单个拣货任务的准备/走动时间
PICK_RATE_PER_MINUTE = 10  # 每分钟拣货件数


def _pending_outbound(db: Session) -> List[OperationTask]:
    return (db.query(OperationTask)
            .filter(OperationTask.status == "待执行", OperationTask.type.in_(OUTBOUND_TASK_TYPES),
                    OperationTask.batch_id.is_(None))
            .order_by(OperationTask.id).all())


@router.get("/operation/batch/suggestions")
def get_batch_suggestions(db: Session = Depends(get_db)):
    """智能批次合并建议：同库区的待执行出库类任务合并为一个批次，节省重复的准备/走动时间"""
    pending = _pending_outbound(db)
    groups = defaultdict(list)
    for t in pending:
        groups[(t.location or "?")[0]].append(t)
    suggestions, saved = [], 0
    for letter in sorted(groups):
        tasks = groups[letter]
        if len(tasks) < 2:
            continue
        total = sum(t.quantity for t in tasks)
        first = min(t.assigned_at for t in tasks if t.assigned_at) if any(t.assigned_at for t in tasks) else None
        saved += (len(tasks) - 1) * TASK_SETUP_MINUTES
        suggestions.append({
            "id": f"BS-{letter}",
            "type": "智能合并",
            "description": f"将{len(tasks)}个{letter}区待执行任务合并为一批次",
            "orders": [t.id for t in tasks],
            "total_items": total,
            "estimated_pick_time": round(TASK_SETUP_MINUTES + total / PICK_RATE_PER_MINUTE),
            "zone": f"{letter}区",
            "priority": min((t.priority for t in tasks), key=lambda p: PRIORITY_ORDER.get(p, 9)),
            "time_window": f"{first:%H}:00-{(first.hour + 2) % 24:02d}:00" if first else None,
            "rules_applied": ["同区域", "时间窗口匹配"],
        })
    individual = sum(TASK_SETUP_MINUTES + t.quantity / PICK_RATE_PER_MINUTE for t in pending)
    return {
        "suggestions": suggestions,
        "stats": {
            "pending_orders": len(pending),
            "suggested_batches": len(suggestions),
            "estimated_time_saved": f"{round(saved / individual * 100) if individual else 0}%",
        },
    }


class BatchCreate(BaseModel):
    task_ids: List[str] = Field(..., min_length=1)

    @field_validator("task_ids")
    @classmethod
    def _unique(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("task_ids 不能重复")
        return v


@router.post("/operation/batch/create")
def create_batch(data: BatchCreate, db: Session = Depends(get_db)):
    """创建批次任务：把待执行的出库类任务归入同一批次"""
    tasks = []
    for tid in data.task_ids:
        t = _get_or_404(db, OperationTask, tid, f"任务 {tid} ")
        if t.status != "待执行" or t.batch_id:
            raise HTTPException(status_code=409, detail=f"任务 {tid} 已开始或已在批次中")
        tasks.append(t)
    now = datetime.now()
    batch = OperationBatch(id=_next_id(db, OperationBatch, f"BATCH{now:%Y%m%d}", 4),
                           zone=(tasks[0].location or "?")[0] + "区", task_ids=data.task_ids,
                           status="待执行", created_at=now)
    db.add(batch)
    for t in tasks:
        t.batch_id = batch.id
        _log(t, "加入批次", "系统", batch.id)
    db.commit()
    return {"success": True, "batch_id": batch.id, "message": "批次创建成功"}


# ========== 车辆管理 ==========

class VehicleIn(BaseModel):
    plate: Optional[str] = Field(None, min_length=1, max_length=20)
    vehicleType: Optional[str] = Field(None, max_length=50)
    driver: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    loadCapacity: Optional[float] = Field(None, ge=0)
    volume: Optional[Union[float, str]] = None
    gpsDevice: Optional[str] = Field(None, max_length=50)
    tempRange: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    location: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = Field(None, ge=-60, le=40)
    battery: Optional[float] = Field(None, ge=0, le=100)

    @field_validator("volume")
    @classmethod
    def _parse_volume(cls, v):
        """前端容积输入框允许 “50立方米” 这类文本，提取其中的数字"""
        if v is None or isinstance(v, (int, float)):
            return v
        m = re.search(r"\d+(\.\d+)?", v)
        if not v.strip():
            return None
        if not m:
            raise ValueError("容积必须是数字")
        return float(m.group())


class VehicleCreate(VehicleIn):
    plate: str = Field(..., min_length=1, max_length=20)


_VEHICLE_FIELDS = {"plate": "plate", "vehicleType": "vehicle_type", "driver": "driver", "phone": "phone",
                   "loadCapacity": "load_capacity", "volume": "volume", "gpsDevice": "gps_device",
                   "tempRange": "temp_range", "status": "status", "location": "location",
                   "temperature": "temperature", "battery": "battery"}


@router.get("/vehicles/list")
def get_vehicles_list(db: Session = Depends(get_db)):
    """获取车辆列表"""
    return [{
        "id": v.id,
        "plate": v.plate,
        "vehicleType": v.vehicle_type or "冷藏车",
        "driver": v.driver,
        "phone": v.phone,
        "loadCapacity": v.load_capacity if v.load_capacity is not None else 5,
        "volume": v.volume,
        "gpsDevice": v.gps_device,
        "tempRange": v.temp_range or "-25°C~5°C",
        "status": v.status,
        "location": v.location,
        "temperature": v.temperature,
        "battery": v.battery,
        "created_at": _fmt(v.created_at, seconds=True),
        "updated_at": _fmt(v.updated_at, seconds=True),
    } for v in db.query(Vehicle).order_by(Vehicle.id.desc()).all()]


@router.post("/vehicles")
def create_vehicle(data: VehicleCreate, db: Session = Depends(get_db)):
    """创建车辆"""
    values = {_VEHICLE_FIELDS[k]: v for k, v in data.model_dump(exclude_none=True).items()}
    defaults = {"vehicle_type": "冷藏车", "load_capacity": 5, "temp_range": "-25°C~5°C", "status": "空闲",
                "location": "", "temperature": -18, "battery": 100}
    vehicle = Vehicle(**{**defaults, **values})
    db.add(vehicle)
    db.commit()
    return {"success": True, "id": vehicle.id, "message": "车辆创建成功"}


@router.put("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: VehicleIn, db: Session = Depends(get_db)):
    """更新车辆（只更新提交的字段）"""
    vehicle = _get_or_404(db, Vehicle, vehicle_id, "车辆")
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "plate" and not value:
            continue
        setattr(vehicle, _VEHICLE_FIELDS[key], value)
    vehicle.updated_at = datetime.now()
    db.commit()
    return {"success": True, "message": "车辆更新成功"}


@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """删除车辆"""
    db.delete(_get_or_404(db, Vehicle, vehicle_id, "车辆"))
    db.commit()
    return {"success": True, "message": "车辆删除成功"}
