"""
智慧农业API - 农场、地块、作物、设备管理
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.smart_agriculture import (
    Land, FarmInfo, IoTDevice, Crop, CropGrowthModel, DecisionRecord, TraceabilityRecord, TraceabilityChainNode,
    EnvironmentReading, IrrigationZone, IrrigationRecord,
)
from app.models.base import Base
from app.database import engine

# 创建表
Base.metadata.create_all(bind=engine)

router = APIRouter()

# ============= 农场管理 =============
@router.get("/farms")
def get_farms(db: Session = Depends(get_db)):
    """获取所有农场"""
    farms = db.query(FarmInfo).all()
    result = []
    for f in farms:
        land_count = db.query(Land).filter(Land.farm_id == f.id).count()
        total_area = sum([l.area or 0 for l in db.query(Land).filter(Land.farm_id == f.id).all()])
        coords = f"{f.lat}°N, {f.lng}°E" if f.lat and f.lng else (f.coords or "")
        result.append({
            "id": f.id,
            "name": f.name,
            "address": f.address,
            "lat": f.lat,
            "lng": f.lng,
            "totalArea": f.total_area or total_area,
            "landCount": land_count,
            "manager": f.manager,
            "phone": f.phone,
            "coords": coords,
            "status": f.status,
            "description": f.description,
            "establishedDate": f.established_date
        })
    return result

@router.get("/farm")
def get_farm_info(db: Session = Depends(get_db)):
    """获取默认农场信息"""
    farm = db.query(FarmInfo).first()
    if not farm:
        # 创建默认农场
        farm = FarmInfo(
            name="智慧生态农场",
            address="山东省济南市历城区",
            lat=36.65,
            lng=117.12,
            total_area=120,
            manager="张建国",
            phone="138****8888",
            coords="36.65°N, 117.12°E",
            status="normal",
            description="专注于有机农业的现代化农场",
            established_date="2020-01-01"
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
    
    land_count = db.query(Land).filter(Land.farm_id == farm.id).count()
    total_area = sum([l.area or 0 for l in db.query(Land).filter(Land.farm_id == farm.id).all()])
    coords = f"{farm.lat}°N, {farm.lng}°E" if farm.lat and farm.lng else (farm.coords or "")
    
    return {
        "id": farm.id,
        "name": farm.name,
        "address": farm.address,
        "lat": farm.lat,
        "lng": farm.lng,
        "totalArea": farm.total_area or total_area,
        "landCount": land_count,
        "manager": farm.manager,
        "phone": farm.phone,
        "coords": coords,
        "status": farm.status,
        "description": farm.description,
        "establishedDate": farm.established_date
    }

@router.post("/farms")
def create_farm(
    name: str = Body(...),
    address: str = Body(""),
    manager: str = Body(""),
    phone: str = Body(""),
    coords: str = Body(""),
    lat: float = Body(None),
    lng: float = Body(None),
    status: str = Body("normal"),
    description: str = Body(""),
    established_date: str = Body(""),
    db: Session = Depends(get_db)
):
    """创建农场"""
    farm = FarmInfo(
        name=name, address=address, manager=manager, phone=phone,
        coords=coords, lat=lat, lng=lng, status=status, description=description, established_date=established_date
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return {"id": farm.id, "message": "农场创建成功"}

@router.put("/farm")
def update_farm_info(
    name: str = Body(...),
    address: str = Body(""),
    manager: str = Body(""),
    phone: str = Body(""),
    coords: str = Body(""),
    lat: float = Body(None),
    lng: float = Body(None),
    status: str = Body("normal"),
    description: str = Body(""),
    established_date: str = Body(""),
    db: Session = Depends(get_db)
):
    """更新农场信息"""
    farm = db.query(FarmInfo).first()
    if not farm:
        farm = FarmInfo(
            name=name, address=address, manager=manager, phone=phone,
            coords=coords, lat=lat, lng=lng, status=status, description=description, established_date=established_date
        )
        db.add(farm)
    else:
        farm.name = name
        farm.address = address
        farm.manager = manager
        farm.phone = phone
        farm.coords = coords
        farm.lat = lat
        farm.lng = lng
        farm.status = status
        farm.description = description
        farm.established_date = established_date
    db.commit()
    return {"message": "农场信息更新成功"}

@router.delete("/farms/{farm_id}")
def delete_farm(farm_id: int, db: Session = Depends(get_db)):
    """删除农场"""
    farm = db.query(FarmInfo).filter(FarmInfo.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="农场不存在")
    
    # 删除农场下的所有地块
    db.query(Land).filter(Land.farm_id == farm_id).delete()
    
    db.delete(farm)
    db.commit()
    return {"message": "删除成功"}

# ============= 地块管理 =============
@router.get("/lands")
def get_lands(farm_id: int = None, db: Session = Depends(get_db)):
    """获取所有地块或指定农场的地块"""
    query = db.query(Land)
    if farm_id:
        query = query.filter(Land.farm_id == farm_id)
    lands = query.all()
    result = []
    for l in lands:
        # 获取所属农场名称
        farm = db.query(FarmInfo).filter(FarmInfo.id == l.farm_id).first()
        farm_name = farm.name if farm else "未知农场"
        
        # 获取关联的作物
        crops = l.crops.split(",") if l.crops else []
        crops = [c.strip() for c in crops if c.strip()]
        
        result.append({
            "id": l.id,
            "farm_id": l.farm_id,
            "farm_name": farm_name,  # 所属农场名称
            "name": l.name,
            "area": l.area,
            "crops": crops,  # 关联作物
            "crop": l.crop,
            "status": l.status
        })
    return result

@router.post("/lands")
def create_land(
    name: str = Body(...),
    area: float = Body(...),
    crop: str = Body(...),
    farm_id: int = Body(None),
    status: str = Body("normal"),
    db: Session = Depends(get_db)
):
    """创建地块"""
    land = Land(name=name, area=area, crop=crop, farm_id=farm_id, status=status)
    db.add(land)
    db.commit()
    db.refresh(land)
    return {"id": land.id, "message": "地块创建成功"}

@router.put("/lands/{land_id}")
def update_land(
    land_id: int,
    name: str = Body(...),
    area: float = Body(...),
    crop: str = Body(...),
    farm_id: int = Body(None),
    status: str = Body("normal"),
    db: Session = Depends(get_db)
):
    """更新地块"""
    land = db.query(Land).filter(Land.id == land_id).first()
    if not land:
        raise HTTPException(status_code=404, detail="地块不存在")
    
    land.name = name
    land.area = area
    land.crop = crop
    land.farm_id = farm_id
    land.status = status
    db.commit()
    return {"message": "地块更新成功"}

@router.delete("/lands/{land_id}")
def delete_land(land_id: int, db: Session = Depends(get_db)):
    """删除地块"""
    land = db.query(Land).filter(Land.id == land_id).first()
    if not land:
        raise HTTPException(status_code=404, detail="地块不存在")
    
    db.delete(land)
    db.commit()
    return {"message": "删除成功"}

# ============= 作物管理 =============
@router.get("/crops")
def get_crops(db: Session = Depends(get_db)):
    """获取所有作物"""
    crops = db.query(Crop).all()
    if not crops:
        # 返回默认作物
        return [
            {"id": 1, "name": "小麦", "category": "粮食", "planting_season": "秋季", "growth_days": 240, "yield_per_mu": 800, "status": "active"},
            {"id": 2, "name": "玉米", "category": "粮食", "planting_season": "春季", "growth_days": 120, "yield_per_mu": 1000, "status": "active"},
            {"id": 3, "name": "水稻", "category": "粮食", "planting_season": "夏季", "growth_days": 150, "yield_per_mu": 1200, "status": "active"},
            {"id": 4, "name": "西红柿", "category": "蔬菜", "planting_season": "春季", "growth_days": 90, "yield_per_mu": 5000, "status": "active"},
            {"id": 5, "name": "黄瓜", "category": "蔬菜", "planting_season": "春季", "growth_days": 60, "yield_per_mu": 4000, "status": "active"},
            {"id": 6, "name": "草莓", "category": "水果", "planting_season": "秋季", "growth_days": 180, "yield_per_mu": 2000, "status": "active"}
        ]
    return [
        {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "planting_season": c.planting_season,
            "growth_days": c.growth_days,
            "yield_per_mu": c.yield_per_mu,
            "status": c.status
        }
        for c in crops
    ]

@router.post("/crops")
def create_crop(
    name: str = Body(...),
    category: str = Body("蔬菜"),
    planting_season: str = Body("春季"),
    growth_days: int = Body(90),
    yield_per_mu: float = Body(1000),
    db: Session = Depends(get_db)
):
    """创建作物"""
    crop = Crop(
        name=name,
        category=category,
        planting_season=planting_season,
        growth_days=growth_days,
        yield_per_mu=yield_per_mu,
        status="active"
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return {"id": crop.id, "message": "作物创建成功"}

@router.put("/crops/{crop_id}")
def update_crop(
    crop_id: int,
    name: str = Body(...),
    category: str = Body(...),
    planting_season: str = Body(...),
    growth_days: int = Body(...),
    yield_per_mu: float = Body(...),
    db: Session = Depends(get_db)
):
    """更新作物"""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="作物不存在")
    
    crop.name = name
    crop.category = category
    crop.planting_season = planting_season
    crop.growth_days = growth_days
    crop.yield_per_mu = yield_per_mu
    db.commit()
    return {"message": "更新成功"}

@router.delete("/crops/{crop_id}")
def delete_crop(crop_id: int, db: Session = Depends(get_db)):
    """删除作物"""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="作物不存在")
    
    db.delete(crop)
    db.commit()
    return {"message": "删除成功"}

# 地块关联作物
@router.put("/lands/{land_id}/crops")
def update_land_crops(
    land_id: int,
    crops: str = Body(..., description="作物ID列表，逗号分隔"),
    db: Session = Depends(get_db)
):
    """更新地块关联的作物"""
    land = db.query(Land).filter(Land.id == land_id).first()
    if not land:
        raise HTTPException(status_code=404, detail="地块不存在")
    
    land.crops = crops
    db.commit()
    return {"message": "作物关联更新成功"}

# ============= 物联网设备 =============
@router.get("/devices")
def get_devices(db: Session = Depends(get_db)):
    """获取所有设备"""
    devices = db.query(IoTDevice).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "type": d.device_type,
            "location": d.location,
            "landId": d.land_id,
            "status": d.status,
            "serialNumber": getattr(d, 'serial_number', None),
            "installDate": getattr(d, 'install_date', None),
            "lastMaintenance": getattr(d, 'last_maintenance', None),
            "lastUpdate": d.last_update.strftime("%Y-%m-%d %H:%M") if d.last_update else "刚刚"
        }
        for d in devices
    ]

@router.post("/devices")
def create_device(
    db: Session = Depends(get_db),
    name: str = Body(...),
    device_type: str = Body(...),
    location: str = Body(""),
    land_id: int = Body(None),
    status: str = Body("online"),
    serial_number: str = Body(""),
    install_date: str = Body(""),
    last_maintenance: str = Body("")
):
    """添加设备"""
    device = IoTDevice(
        name=name,
        device_type=device_type,
        location=location,
        land_id=land_id,
        status=status,
        serial_number=serial_number,
        install_date=install_date,
        last_maintenance=last_maintenance,
        last_update=datetime.now()
    )

    db.add(device)
    db.commit()
    db.refresh(device)
    return {"id": device.id, "message": "设备添加成功"}

@router.put("/devices/{device_id}")
def update_device(
    device_id: int,
    name: str = None,
    device_type: str = None,
    location: str = None,
    land_id: int = None,
    status: str = None,
    serial_number: str = None,
    install_date: str = None,
    last_maintenance: str = None,
    db: Session = Depends(get_db)
):
    """更新设备"""
    device = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    if name is not None:
        device.name = name
    if device_type is not None:
        device.device_type = device_type
    if location is not None:
        device.location = location
    if land_id is not None:
        device.land_id = land_id
    if status is not None:
        device.status = status
    if serial_number is not None and hasattr(device, 'serial_number'):
        device.serial_number = serial_number
    if install_date is not None and hasattr(device, 'install_date'):
        device.install_date = install_date
    if last_maintenance is not None and hasattr(device, 'last_maintenance'):
        device.last_maintenance = last_maintenance

    device.last_update = datetime.now()
    db.commit()
    return {"message": "设备更新成功"}

@router.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    device = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    db.delete(device)
    db.commit()
    return {"message": "删除成功"}

# ============= 传感器数据 / 灌溉 / 分析（均来自数据库） =============

SOIL_OPTIMAL = {  # 土壤指标适宜区间，用于计算土壤健康评分
    "soil_ph": (6.0, 7.5),
    "soil_moisture": (40, 75),
    "nitrogen": (100, 200),
    "phosphorus": (30, 80),
    "potassium": (150, 250),
}
LAND_YIELD_FACTOR = {"normal": 1.0, "warning": 0.85}  # 其他状态按 0.6 计


def _latest_readings(db: Session, before: Optional[datetime] = None) -> List[EnvironmentReading]:
    """每个监测站最新（或指定时间之前最新）的一条读数，按 sensor_id 排序"""
    sub = db.query(
        EnvironmentReading.sensor_id,
        func.max(EnvironmentReading.recorded_at).label("ts"),
    )
    if before is not None:
        sub = sub.filter(EnvironmentReading.recorded_at <= before)
    sub = sub.group_by(EnvironmentReading.sensor_id).subquery()
    return (
        db.query(EnvironmentReading)
        .join(sub, (EnvironmentReading.sensor_id == sub.c.sensor_id) & (EnvironmentReading.recorded_at == sub.c.ts))
        .order_by(EnvironmentReading.sensor_id)
        .all()
    )


def _ts(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _avg(values) -> Optional[float]:
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _soil_score(readings: List[EnvironmentReading]) -> Optional[float]:
    """土壤健康评分：每项指标在适宜区间中点得 100 分，到区间边界线性降到 60 分，
    区间外继续按同样斜率下降（最低 0），取各站各项的平均值"""
    scores = []
    for r in readings:
        for field, (lo, hi) in SOIL_OPTIMAL.items():
            v = getattr(r, field)
            if v is None:
                continue
            mid, half = (lo + hi) / 2, (hi - lo) / 2
            scores.append(max(0.0, 100.0 - 40.0 * abs(v - mid) / half))
    return _avg(scores)


def _soil_status(score: float) -> str:
    if score >= 90:
        return "优秀"
    if score >= 75:
        return "良好"
    if score >= 60:
        return "一般"
    return "较差"


@router.get("/soil")
def get_soil_data(db: Session = Depends(get_db)):
    """获取土壤监测数据（每个监测站最新读数）"""
    return [{
        "id": idx + 1,
        "sensor_id": r.sensor_id,
        "location": r.location,
        "land_id": r.land_id,
        "temperature": r.soil_temperature,
        "humidity": r.soil_moisture,
        "ph": r.soil_ph,
        "nitrogen": r.nitrogen,
        "phosphorus": r.phosphorus,
        "potassium": r.potassium,
        "conductivity": r.conductivity,
        "timestamp": _ts(r.recorded_at),
    } for idx, r in enumerate(_latest_readings(db))]


@router.get("/weather")
def get_weather_data(db: Session = Depends(get_db)):
    """获取气象数据（每个监测站最新读数）"""
    return [{
        "id": idx + 1,
        "sensor_id": r.sensor_id,
        "location": r.location,
        "land_id": r.land_id,
        "temperature": r.air_temperature,
        "humidity": r.air_humidity,
        "wind_speed": r.wind_speed,
        "wind_direction": r.wind_direction,
        "precipitation": r.rainfall,
        "atmospheric_pressure": r.pressure,
        "uv_index": r.uv_index,
        "visibility": r.visibility,
        "light": r.light,
        "co2": r.co2,
        "timestamp": _ts(r.recorded_at),
    } for idx, r in enumerate(_latest_readings(db))]


@router.get("/monitor")
def get_monitor_summary(db: Session = Depends(get_db)):
    """环境监测概览：各监测站最新读数的平均值，降雨量为最近 24 小时累计"""
    latest = _latest_readings(db)
    if not latest:
        return {"temperature": None, "humidity": None, "soilMoisture": None, "light": None,
                "co2": None, "rainfall": None, "stationCount": 0, "timestamp": None}
    newest = max(r.recorded_at for r in latest)
    rain_rows = db.query(EnvironmentReading.sensor_id, func.sum(EnvironmentReading.rainfall)).filter(
        EnvironmentReading.recorded_at > newest - timedelta(hours=24)
    ).group_by(EnvironmentReading.sensor_id).all()

    def r1(v, nd=1):
        return round(v, nd) if v is not None else None

    return {
        "temperature": r1(_avg(r.air_temperature for r in latest)),
        "humidity": r1(_avg(r.air_humidity for r in latest)),
        "soilMoisture": r1(_avg(r.soil_moisture for r in latest)),
        "light": r1(_avg(r.light for r in latest), 0),
        "co2": r1(_avg(r.co2 for r in latest), 0),
        "rainfall": r1(_avg(total or 0 for _, total in rain_rows)),
        "stationCount": len(latest),
        "timestamp": _ts(newest),
    }


@router.get("/readings")
def get_readings(
    sensor_id: Optional[str] = None,
    land_id: Optional[int] = None,
    hours: int = Query(24, ge=1, le=24 * 31),
    db: Session = Depends(get_db),
):
    """环境读数时间序列（最近 N 小时，相对最新一条读数），按时间升序"""
    base = db.query(EnvironmentReading)
    if sensor_id:
        base = base.filter(EnvironmentReading.sensor_id == sensor_id)
    if land_id:
        base = base.filter(EnvironmentReading.land_id == land_id)
    newest = base.with_entities(func.max(EnvironmentReading.recorded_at)).scalar()
    if newest is None:
        return []
    rows = base.filter(EnvironmentReading.recorded_at > newest - timedelta(hours=hours)).order_by(
        EnvironmentReading.recorded_at, EnvironmentReading.sensor_id
    ).all()
    return [{
        "sensor_id": r.sensor_id,
        "location": r.location,
        "land_id": r.land_id,
        "timestamp": _ts(r.recorded_at),
        "air_temperature": r.air_temperature,
        "air_humidity": r.air_humidity,
        "rainfall": r.rainfall,
        "light": r.light,
        "co2": r.co2,
        "soil_temperature": r.soil_temperature,
        "soil_moisture": r.soil_moisture,
        "ph": r.soil_ph,
        "nitrogen": r.nitrogen,
        "phosphorus": r.phosphorus,
        "potassium": r.potassium,
    } for r in rows]


def _irrigation_item(db: Session, zone: IrrigationZone) -> dict:
    last_done = db.query(IrrigationRecord).filter(
        IrrigationRecord.zone_id == zone.id, IrrigationRecord.ended_at.isnot(None)
    ).order_by(IrrigationRecord.started_at.desc()).first()
    running = zone.status == "运行中"
    return {
        "id": zone.id,
        "zone": zone.name,
        "land_id": zone.land_id,
        "status": zone.status,
        "water_flow": zone.rated_flow if running else 0,
        "pressure": zone.pressure,
        "duration": zone.planned_duration if running else 0,
        "moisture_before": last_done.moisture_before if last_done else None,
        "moisture_after": last_done.moisture_after if last_done else None,
        "auto_mode": bool(zone.auto_mode),
        "started_at": _ts(zone.started_at) if running else None,
        "timestamp": _ts(zone.updated_at),
    }


@router.get("/irrigation")
def get_irrigation_data(db: Session = Depends(get_db)):
    """获取智能灌溉数据（分区当前状态 + 最近一次完成灌溉的前后土壤湿度）"""
    zones = db.query(IrrigationZone).order_by(IrrigationZone.id).all()
    return [_irrigation_item(db, z) for z in zones]


@router.get("/irrigation/records")
def get_irrigation_records(zone_id: Optional[int] = None, limit: int = Query(50, ge=1, le=500),
                           db: Session = Depends(get_db)):
    """灌溉历史记录（最新在前）"""
    q = db.query(IrrigationRecord)
    if zone_id:
        q = q.filter(IrrigationRecord.zone_id == zone_id)
    rows = q.order_by(IrrigationRecord.started_at.desc(), IrrigationRecord.id.desc()).limit(limit).all()
    return [{
        "id": r.id,
        "zone_id": r.zone_id,
        "land_id": r.land_id,
        "mode": r.mode,
        "started_at": _ts(r.started_at),
        "ended_at": _ts(r.ended_at),
        "duration": r.duration,
        "water_volume": r.water_volume,
        "moisture_before": r.moisture_before,
        "moisture_after": r.moisture_after,
    } for r in rows]


class IrrigationControl(BaseModel):
    action: str  # start / stop
    duration: Optional[int] = None  # start 时的计划时长(分钟)
    auto_mode: Optional[bool] = None


def _latest_moisture(db: Session, land_id: Optional[int]) -> Optional[float]:
    if land_id is None:
        return None
    r = db.query(EnvironmentReading).filter(EnvironmentReading.land_id == land_id).order_by(
        EnvironmentReading.recorded_at.desc()
    ).first()
    return r.soil_moisture if r else None


@router.post("/irrigation/{zone_id}/control")
def control_irrigation(zone_id: int, body: IrrigationControl, db: Session = Depends(get_db)):
    """启动 / 停止灌溉分区，并写入灌溉记录"""
    zone = db.query(IrrigationZone).filter(IrrigationZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="灌溉分区不存在")
    if body.action not in ("start", "stop"):
        raise HTTPException(status_code=400, detail="action 只能为 start 或 stop")
    now = datetime.now()
    if body.auto_mode is not None:
        zone.auto_mode = body.auto_mode
    open_record = db.query(IrrigationRecord).filter(
        IrrigationRecord.zone_id == zone.id, IrrigationRecord.ended_at.is_(None)
    ).order_by(IrrigationRecord.started_at.desc()).first()

    if body.action == "start":
        if zone.status == "运行中":
            raise HTTPException(status_code=400, detail="该分区已在运行")
        zone.status = "运行中"
        zone.started_at = now
        zone.planned_duration = body.duration or 45
        db.add(IrrigationRecord(
            zone_id=zone.id, land_id=zone.land_id, mode="manual", started_at=now,
            moisture_before=_latest_moisture(db, zone.land_id),
        ))
    else:
        if zone.status != "运行中":
            raise HTTPException(status_code=400, detail="该分区未在运行")
        if open_record:
            minutes = max(0, int((now - open_record.started_at).total_seconds() // 60))
            open_record.ended_at = now
            open_record.duration = minutes
            open_record.water_volume = round((zone.rated_flow or 0) * minutes / 60, 2)
            # 灌溉后湿度取该地块最新的传感器读数
            open_record.moisture_after = _latest_moisture(db, zone.land_id)
        zone.status = "停止"
        zone.planned_duration = 0
        zone.started_at = None
    zone.updated_at = now
    db.commit()
    db.refresh(zone)
    return _irrigation_item(db, zone)


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """农业分析数据：由地块、作物、传感器读数、灌溉记录计算"""
    # 土壤健康：最新读数 vs 24 小时前读数
    latest = _latest_readings(db)
    score = _soil_score(latest)
    trend = "持平"
    if latest and score is not None:
        prev = _soil_score(_latest_readings(db, max(r.recorded_at for r in latest) - timedelta(hours=24)))
        if prev is not None and abs(score - prev) >= 0.5:
            trend = "上升" if score > prev else "下降"

    # 用水量(m³)：按灌溉开始日期统计
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def water_between(start: datetime, end: datetime) -> float:
        return db.query(func.coalesce(func.sum(IrrigationRecord.water_volume), 0)).filter(
            IrrigationRecord.started_at >= start, IrrigationRecord.started_at < end
        ).scalar() or 0

    week_total = water_between(today - timedelta(days=7), today)
    done = db.query(IrrigationRecord).filter(
        IrrigationRecord.ended_at.isnot(None),
        IrrigationRecord.moisture_before.isnot(None),
        IrrigationRecord.moisture_after.isnot(None),
    ).all()
    # 灌溉效率：灌后土壤湿度达到适宜下限以上且较灌前提升 ≥10 个百分点的灌溉次数占比
    effective = [r for r in done
                 if r.moisture_after >= SOIL_OPTIMAL["soil_moisture"][0] and r.moisture_after - r.moisture_before >= 10]
    efficiency = round(len(effective) / len(done) * 100) if done else 0

    # 作物状态：按地块状态的面积占比
    lands = db.query(Land).all()
    total_area = sum(l.area or 0 for l in lands)

    def area_pct(pred) -> float:
        if not total_area:
            return 0
        return round(sum(l.area or 0 for l in lands if pred(l.status or "normal")) / total_area * 100)

    # 产量预测(吨)：地块面积 × 作物标准亩产(斤) × 地块状态系数；last_season 为按标准亩产计算的基准产量
    yields = {c.name: c.yield_per_mu or 0 for c in db.query(Crop).all()}
    baseline = sum((l.area or 0) * yields.get(l.crop, 0) for l in lands) / 2000
    current = sum((l.area or 0) * yields.get(l.crop, 0) * LAND_YIELD_FACTOR.get(l.status or "normal", 0.6)
                  for l in lands) / 2000

    return {
        "soil_health": {
            "score": round(score) if score is not None else 0,
            "status": _soil_status(score) if score is not None else "无数据",
            "trend": trend,
        },
        "water_usage": {
            "today": round(water_between(today, today + timedelta(days=1)), 1),
            "yesterday": round(water_between(today - timedelta(days=1), today), 1),
            "week_avg": round(week_total / 7, 1),
            "efficiency": efficiency,
        },
        "crop_status": {
            "total_area": round(total_area, 1),
            "healthy": area_pct(lambda s: s == "normal"),
            "warning": area_pct(lambda s: s == "warning"),
            "critical": area_pct(lambda s: s not in ("normal", "warning")),
        },
        "yield_prediction": {
            "current_season": round(current, 1),
            "last_season": round(baseline, 1),
            "change": round((current - baseline) / baseline * 100, 1) if baseline else 0,
        },
    }

# ============= 智能决策系统 API =============

@router.get("/decision/models")
def get_crop_models(db: Session = Depends(get_db)):
    """获取农作物生长模型列表"""
    models = db.query(CropGrowthModel).all()
    return [{
        "id": m.id,
        "cropName": m.crop_name,
        "cropType": m.crop_type,
        "growthStages": m.growth_stages,
        "baseTemp": m.base_temp,
        "optimalTempMin": m.optimal_temp_min,
        "optimalTempMax": m.optimal_temp_max,
        "optimalHumidityMin": m.optimal_humidity_min,
        "optimalHumidityMax": m.optimal_humidity_max,
        "waterRequirement": m.water_requirement,
        "fertilizerRequirement": m.fertilizer_requirement,
        "expectedYield": m.expected_yield,
        "predictionAccuracy": m.prediction_accuracy,
        "modelVersion": m.model_version,
        "status": m.status,
        "description": m.description
    } for m in models]

@router.post("/decision/models")
def create_crop_model(data: dict = Body(...), db: Session = Depends(get_db)):
    """创建农作物生长模型"""
    model = CropGrowthModel(
        crop_name=data.get("cropName"),
        crop_type=data.get("cropType"),
        growth_stages=data.get("growthStages"),
        base_temp=data.get("baseTemp", 10),
        optimal_temp_min=data.get("optimalTempMin", 20),
        optimal_temp_max=data.get("optimalTempMax", 30),
        optimal_humidity_min=data.get("optimalHumidityMin", 60),
        optimal_humidity_max=data.get("optimalHumidityMax", 80),
        water_requirement=data.get("waterRequirement", 500),
        fertilizer_requirement=data.get("fertilizerRequirement", 0),
        expected_yield=data.get("expectedYield", 0),
        prediction_accuracy=data.get("predictionAccuracy", 95),
        model_version=data.get("modelVersion", "v1.0"),
        description=data.get("description")
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return {"id": model.id, "message": "模型创建成功"}

@router.get("/decision/models/{model_id}")
def get_crop_model(model_id: int, db: Session = Depends(get_db)):
    """获取单个作物模型详情"""
    model = db.query(CropGrowthModel).filter(CropGrowthModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return {
        "id": model.id,
        "cropName": model.crop_name,
        "cropType": model.crop_type,
        "growthStages": model.growth_stages,
        "baseTemp": model.base_temp,
        "optimalTempMin": model.optimal_temp_min,
        "optimalTempMax": model.optimal_temp_max,
        "optimalHumidityMin": model.optimal_humidity_min,
        "optimalHumidityMax": model.optimal_humidity_max,
        "waterRequirement": model.water_requirement,
        "fertilizerRequirement": model.fertilizer_requirement,
        "expectedYield": model.expected_yield,
        "predictionAccuracy": model.prediction_accuracy,
        "modelVersion": model.model_version,
        "status": model.status,
        "description": model.description
    }

@router.put("/decision/models/{model_id}")
def update_crop_model(model_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """更新作物模型"""
    model = db.query(CropGrowthModel).filter(CropGrowthModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    db.commit()
    return {"message": "更新成功"}

@router.delete("/decision/models/{model_id}")
def delete_crop_model(model_id: int, db: Session = Depends(get_db)):
    """删除作物模型"""
    model = db.query(CropGrowthModel).filter(CropGrowthModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    db.delete(model)
    db.commit()
    return {"message": "删除成功"}

@router.get("/decision/records")
def get_decision_records(land_id: int = None, db: Session = Depends(get_db)):
    """获取智能决策记录"""
    query = db.query(DecisionRecord)
    if land_id:
        query = query.filter(DecisionRecord.land_id == land_id)
    records = query.order_by(DecisionRecord.created_at.desc()).all()
    return [{
        "id": r.id,
        "landId": r.land_id,
        "cropModelId": r.crop_model_id,
        "decisionType": r.decision_type,
        "currentValue": r.current_value,
        "recommendedValue": r.recommended_value,
        "recommendation": r.recommendation,
        "visualizationData": r.visualization_data,
        "confidence": r.confidence,
        "executed": r.executed,
        "executedAt": r.executed_at.isoformat() if r.executed_at else None,
        "createdAt": r.created_at.isoformat() if r.created_at else None
    } for r in records]

@router.post("/decision/generate")
def generate_decision(data: dict = Body(...), db: Session = Depends(get_db)):
    """生成智能决策建议"""
    land_id = data.get("landId")
    decision_type = data.get("decisionType", "灌溉")
    recommendations = {
        "灌溉": {"recommendation": "建议当前土壤湿度偏低(35%)，需进行灌溉", "recommendedValue": 25, "visualizationData": '{"type": "irrigation_heatmap"}'},
        "施肥": {"recommendation": "氮含量不足，建议追施尿素5kg/亩", "recommendedValue": 5, "visualizationData": '{"type": "fertilizer_prescription"}'},
        "喷药": {"recommendation": "发现轻度病虫害，建议喷施生物农药", "recommendedValue": 1, "visualizationData": '{"type": "spray_status"}'},
        "收获预警": {"recommendation": "预计7天后进入收获期，请提前准备", "recommendedValue": 7, "visualizationData": '{"type": "harvest_timeline"}'}
    }
    rec = recommendations.get(decision_type, recommendations["灌溉"])
    record = DecisionRecord(
        land_id=land_id,
        decision_type=decision_type,
        current_value=data.get("currentValue", 35),
        recommended_value=rec["recommendedValue"],
        recommendation=rec["recommendation"],
        visualization_data=rec["visualizationData"],
        confidence=0.95
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "decisionType": record.decision_type, "recommendation": record.recommendation, "recommendedValue": record.recommended_value, "confidence": record.confidence}

@router.post("/decision/records/{record_id}/execute")
def execute_decision(record_id: int, db: Session = Depends(get_db)):
    """执行决策"""
    record = db.query(DecisionRecord).filter(DecisionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="决策记录不存在")
    record.executed = True
    record.executed_at = datetime.now()
    db.commit()
    return {"message": "执行成功"}

# ============= 全产业链追溯系统 API =============

@router.get("/traceability/records")
def get_traceability_records(category: str = None, status: str = None, db: Session = Depends(get_db)):
    """获取追溯记录列表"""
    query = db.query(TraceabilityRecord)
    if category:
        query = query.filter(TraceabilityRecord.category == category)
    if status:
        query = query.filter(TraceabilityRecord.status == status)
    records = query.order_by(TraceabilityRecord.created_at.desc()).all()
    return [{
        "id": r.id,
        "productName": r.product_name,
        "productBatch": r.product_batch,
        "category": r.category,
        "originFarm": r.origin_farm,
        "originAddress": r.origin_address,
        "plantingDate": r.planting_date,
        "harvestDate": r.harvest_date,
        "processingDate": r.processing_date,
        "processingFactory": r.processing_factory,
        "logisticsCompany": r.logistics_company,
        "logisticsNo": r.logistics_no,
        "warehouse": r.warehouse,
        "retailOutlet": r.retail_outlet,
        "saleDate": r.sale_date,
        "certifications": r.certifications,
        "traceCode": r.trace_code,
        "qrCode": r.qr_code,
        "status": r.status
    } for r in records]

@router.post("/traceability/records")
def create_traceability_record(data: dict = Body(...), db: Session = Depends(get_db)):
    """创建追溯记录"""
    import uuid
    trace_code = f"TRACE-{uuid.uuid4().hex[:12].upper()}"
    record = TraceabilityRecord(
        product_name=data.get("productName"),
        product_batch=data.get("productBatch"),
        category=data.get("category"),
        origin_farm=data.get("originFarm"),
        origin_address=data.get("originAddress"),
        planting_date=data.get("plantingDate"),
        harvest_date=data.get("harvestDate"),
        processing_date=data.get("processingDate"),
        processing_factory=data.get("processingFactory"),
        logistics_company=data.get("logisticsCompany"),
        logistics_no=data.get("logisticsNo"),
        warehouse=data.get("warehouse"),
        retail_outlet=data.get("retailOutlet"),
        sale_date=data.get("saleDate"),
        certifications=data.get("certifications"),
        trace_code=trace_code,
        qr_code=f"/api/traceability/qr/{trace_code}.png",
        status="active"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "traceCode": record.trace_code, "message": "追溯记录创建成功"}

@router.get("/traceability/records/{record_id}")
def get_traceability_record(record_id: int, db: Session = Depends(get_db)):
    """获取追溯记录详情"""
    record = db.query(TraceabilityRecord).filter(TraceabilityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="追溯记录不存在")
    nodes = db.query(TraceabilityChainNode).filter(TraceabilityChainNode.trace_record_id == record_id).order_by(TraceabilityChainNode.created_at).all()
    return {
        "id": record.id,
        "productName": record.product_name,
        "productBatch": record.product_batch,
        "category": record.category,
        "originFarm": record.origin_farm,
        "plantingDate": record.planting_date,
        "harvestDate": record.harvest_date,
        "traceCode": record.trace_code,
        "status": record.status,
        "nodes": [{"id": n.id, "nodeType": n.node_type, "nodeName": n.node_name, "description": n.description, "timestamp": n.timestamp} for n in nodes]
    }

@router.get("/traceability/code/{trace_code}")
def get_traceability_by_code(trace_code: str, db: Session = Depends(get_db)):
    """通过追溯码查询"""
    record = db.query(TraceabilityRecord).filter(TraceabilityRecord.trace_code == trace_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="追溯码不存在")
    nodes = db.query(TraceabilityChainNode).filter(TraceabilityChainNode.trace_record_id == record.id).order_by(TraceabilityChainNode.created_at).all()
    return {"productName": record.product_name, "productBatch": record.product_batch, "originFarm": record.origin_farm, "traceCode": record.trace_code, "status": record.status, "nodes": [{"nodeType": n.node_type, "nodeName": n.node_name, "timestamp": n.timestamp} for n in nodes]}

@router.post("/traceability/records/{record_id}/nodes")
def add_traceability_node(record_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """添加追溯节点"""
    record = db.query(TraceabilityRecord).filter(TraceabilityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="追溯记录不存在")
    node = TraceabilityChainNode(
        trace_record_id=record_id,
        node_type=data.get("nodeType"),
        node_name=data.get("nodeName"),
        description=data.get("description"),
        operator=data.get("operator"),
        location=data.get("location"),
        data=data.get("data"),
        image_url=data.get("imageUrl"),
        timestamp=datetime.now().isoformat()
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return {"id": node.id, "message": "节点添加成功"}

@router.put("/traceability/records/{record_id}")
def update_traceability_record(record_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    """更新追溯记录"""
    record = db.query(TraceabilityRecord).filter(TraceabilityRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="追溯记录不存在")
    for key, value in data.items():
        if hasattr(record, key):
            setattr(record, key, value)
    db.commit()
    return {"message": "更新成功"}
