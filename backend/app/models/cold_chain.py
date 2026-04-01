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


# Warehouse model removed - using the one from smart_agriculture.py
# The cold_chain API queries the warehouses table directly via raw SQL
