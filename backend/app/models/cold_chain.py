"""
冷链运输模型
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text
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


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plate = Column(String(20), nullable=False)
    vehicle_type = Column(String(50), default="冷藏车")
    driver = Column(String(50))
    phone = Column(String(20))
    load_capacity = Column(Float, default=5)
    volume = Column(Float)
    gps_device = Column(String(50))
    temp_range = Column(String(20), default="-25°C~5°C")
    status = Column(String(20), default="空闲")
    location = Column(String(100))
    temperature = Column(Float, default=-18)
    battery = Column(Float, default=100)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CargoOwner(Base):
    __tablename__ = "cargo_owners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    contact = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    status = Column(String(20), default="正常")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


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
