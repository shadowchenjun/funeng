"""
智慧农业API - 农场、地块、作物、设备管理
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import random

from app.database import get_db
from app.models.smart_agriculture import Land, FarmInfo, IoTDevice, Warehouse, Member, Campaign, Crop
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
    if not devices:
        # 返回默认设备
        return [
            {"id": 1, "name": "温度传感器-01", "type": "temp", "location": "A区大棚1", "status": "online", "lastUpdate": "刚刚"},
            {"id": 2, "name": "湿度传感器-01", "type": "humidity", "location": "A区大棚1", "status": "online", "lastUpdate": "刚刚"},
            {"id": 3, "name": "土壤传感器-01", "type": "soil", "location": "B区大棚2", "status": "warning", "lastUpdate": "刚刚"},
            {"id": 4, "name": "气象站-01", "type": "weather", "location": "园区中心", "status": "online", "lastUpdate": "刚刚"},
            {"id": 5, "name": "摄像头-01", "type": "camera", "location": "C区露天", "status": "offline", "lastUpdate": "1小时前"}
        ]
    return [
        {
            "id": d.id,
            "name": d.name,
            "type": d.device_type,
            "location": d.location,
            "status": d.status,
            "lastUpdate": d.last_update.strftime("%Y-%m-%d %H:%M") if d.last_update else "刚刚"
        }
        for d in devices
    ]

@router.post("/devices")
def create_device(
    name: str,
    device_type: str,
    location: str,
    db: Session = Depends(get_db)
):
    """添加设备"""
    device = IoTDevice(
        name=name,
        device_type=device_type,
        location=location,
        status="online",
        last_update=datetime.now()
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return {"id": device.id, "message": "设备添加成功"}

@router.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    device = db.query(IoTDevice).filter(IoTDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    db.delete(device)
    db.commit()
    return {"message": "删除成功"}

# ============= 以下是原有的传感器数据API =============

@router.get("/soil")
def get_soil_data():
    """获取土壤监测数据"""
    sensors = ["S001", "S002", "S003", "S004"]
    locations = ["东区1号田", "西区1号田", "东区2号田", "西区2号田"]
    
    data = []
    for i, (sensor_id, location) in enumerate(zip(sensors, locations)):
        data.append({
            "id": i + 1,
            "sensor_id": sensor_id,
            "location": location,
            "temperature": round(18 + random.uniform(-2, 8), 1),
            "humidity": round(65 + random.uniform(-15, 20), 1),
            "ph": round(6.5 + random.uniform(-0.5, 0.8), 1),
            "nitrogen": round(120 + random.uniform(-30, 50), 1),
            "phosphorus": round(45 + random.uniform(-15, 20), 1),
            "potassium": round(180 + random.uniform(-40, 60), 1),
            "conductivity": round(1.2 + random.uniform(-0.3, 0.5), 2),
            "timestamp": datetime.now().isoformat()
        })
    return data

@router.get("/weather")
def get_weather_data():
    """获取气象数据"""
    locations = ["园区1号", "园区2号", "园区3号", "园区4号"]
    
    data = []
    for i, location in enumerate(locations):
        data.append({
            "id": i + 1,
            "location": location,
            "temperature": round(15 + random.uniform(-5, 15), 1),
            "humidity": round(60 + random.uniform(-15, 25), 1),
            "wind_speed": round(random.uniform(0, 20), 1),
            "wind_direction": random.choice(["北风", "东北风", "东风", "东南风", "南风"]),
            "precipitation": round(random.uniform(0, 5), 1),
            "atmospheric_pressure": round(1013 + random.uniform(-20, 30), 0),
            "uv_index": round(random.uniform(1, 11), 0),
            "visibility": round(5 + random.uniform(-2, 8), 1),
            "timestamp": datetime.now().isoformat()
        })
    return data

@router.get("/irrigation")
def get_irrigation_data():
    """获取智能灌溉数据"""
    zones = ["灌溉区A", "灌溉区B", "灌溉区C", "灌溉区D"]
    statuses = ["运行中", "停止", "运行中", "停止"]
    
    data = []
    for i, (zone, status) in enumerate(zip(zones, statuses)):
        data.append({
            "id": i + 1,
            "zone": zone,
            "status": status,
            "water_flow": round(random.uniform(10, 50), 1) if status == "运行中" else 0,
            "pressure": round(random.uniform(2, 5), 1),
            "duration": random.randint(0, 120) if status == "运行中" else 0,
            "moisture_before": round(35 + random.uniform(-5, 10), 1),
            "moisture_after": round(65 + random.uniform(-5, 10), 1),
            "auto_mode": random.choice([True, False]),
            "timestamp": datetime.now().isoformat()
        })
    return data

@router.get("/analytics")
def get_analytics():
    """获取农业分析数据"""
    return {
        "soil_health": {
            "score": round(random.uniform(75, 95), 0),
            "status": "良好",
            "trend": "上升"
        },
        "water_usage": {
            "today": round(random.uniform(100, 500), 0),
            "yesterday": round(random.uniform(100, 500), 0),
            "week_avg": round(random.uniform(100, 500), 0),
            "efficiency": round(random.uniform(75, 95), 0)
        },
        "crop_status": {
            "total_area": round(random.uniform(500, 2000), 0),
            "healthy": round(random.uniform(80, 95), 0),
            "warning": round(random.uniform(3, 15), 0),
            "critical": round(random.uniform(0, 5), 0)
        },
        "yield_prediction": {
            "current_season": round(random.uniform(800, 1500), 0),
            "last_season": round(random.uniform(800, 1500), 0),
            "change": round(random.uniform(-10, 20), 1)
        }
    }
