"""
smart_agriculture 默认数据（表为空时写入固定数据，不使用随机数）

- environment_readings: 每个监测站最近 7 天逐小时读数，由固定参数的正弦/指数函数生成
- irrigation_zones / irrigation_records: 灌溉分区与历史灌溉记录，与土壤湿度曲线一致
  （每次灌溉后土壤湿度回升，随后按指数衰减）
- 数字营销（电商订单/渠道流量）默认数据也从这里调用写入，
  因为 main.py 只调用 seed_smart_agriculture（见 app/seeds/digital_marketing.py）
"""
import math
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.smart_agriculture import (
    EnvironmentReading, IrrigationRecord, IrrigationZone, Land,
)
from app.seeds.digital_marketing import seed_digital_marketing

HOURS = 7 * 24
FALLBACK_STATIONS = ["东区1号田", "西区1号田", "东区2号田", "西区2号田"]
WIND_DIRECTIONS = ["北风", "东北风", "东风", "东南风", "南风", "西南风", "西风", "西北风"]
RAIN_DAYS = {2, 5}  # 相对起始日的第几天午后有降雨

# 灌溉分区参数: (名称, 额定流量 m³/h, 管网压力 bar, 单次时长 min, 自动模式)
ZONES = [
    ("灌溉区A", 18.0, 3.2, 45, True),
    ("灌溉区B", 22.0, 3.6, 50, True),
    ("灌溉区C", 26.0, 2.8, 55, False),
    ("灌溉区D", 30.0, 4.1, 60, True),
]
RUNNING_ZONES = {0, 2}  # 当前正在运行的分区下标


def _stations(db: Session):
    lands = db.query(Land).order_by(Land.id).limit(4).all()
    stations = [(l.id, l.name) for l in lands]
    for name in FALLBACK_STATIONS[len(stations):]:
        stations.append((None, name))
    return stations


def _is_irrigation_hour(t0: datetime, h: int, i: int) -> bool:
    ts = t0 + timedelta(hours=h)
    day = (ts.date() - t0.date()).days
    return ts.hour == 6 and (day + i) % 2 == 0


# 各监测站土壤参数: (湿度下限, 灌后增幅, 衰减时间常数 h, 初始含氮量 mg/kg)
SOIL_PARAMS = [(36.0, 32.0, 24.0, 135.0), (40.0, 28.0, 30.0, 142.0), (38.0, 30.0, 36.0, 128.0), (34.0, 33.0, 28.0, 112.0)]


def _moisture(i: int, hours_since_irrigation: float, diurnal: float) -> float:
    floor, amp, tau, _ = SOIL_PARAMS[i]
    return floor + amp * math.exp(-hours_since_irrigation / tau) - 2 * diurnal


def _reading(t0: datetime, h: int, i: int, land_id, location: str, since_irr: float) -> EnvironmentReading:
    ts = t0 + timedelta(hours=h)
    hod = ts.hour
    day = (ts.date() - t0.date()).days
    greenhouse = i < 2
    diurnal = math.sin(2 * math.pi * (hod - 9) / 24)  # 15:00 最高
    sun = max(0.0, math.sin(math.pi * (hod - 6) / 12))  # 6:00-18:00 日照
    rain = 0.0
    if day in RAIN_DAYS and 13 <= hod <= 17:
        rain = 2.4 * math.sin(math.pi * (hod - 12) / 6)
    return EnvironmentReading(
        land_id=land_id,
        sensor_id=f"S{i + 1:03d}",
        location=location,
        recorded_at=ts,
        air_temperature=round(21 + 0.8 * i + 6 * diurnal + 1.5 * math.sin(2 * math.pi * h / HOURS), 1),
        air_humidity=round(66 - 12 * diurnal + 3 * math.cos(2 * math.pi * h / 72 + i) + (10 if rain else 0), 1),
        wind_speed=round(3 + 1.5 * (1 + math.sin(2 * math.pi * (hod - 14) / 24)) + 0.8 * math.sin(h / 11 + i), 1),
        wind_direction=WIND_DIRECTIONS[(day + i) % len(WIND_DIRECTIONS)],
        rainfall=round(rain, 1),
        pressure=round(1013 + 4 * math.sin(2 * math.pi * h / 96) - (3 if rain else 0), 0),
        uv_index=round(9 * sun * (0.4 if rain else 1), 0),
        visibility=round(12 + 2 * math.sin(2 * math.pi * h / 48 + i) - (5 if rain else 0), 1),
        light=round(55000 * sun * (0.6 if greenhouse else 1) * (0.3 if rain else 1), 0),
        co2=round(420 + (80 if greenhouse else 0) + 60 * math.cos(2 * math.pi * (hod - 3) / 24), 0),
        soil_temperature=round(18 + 0.5 * i + 3 * math.sin(2 * math.pi * (hod - 11) / 24), 1),
        soil_moisture=round(_moisture(i, since_irr, diurnal), 1),
        soil_ph=round(6.5 + 0.3 * math.sin(i * 1.3) + 0.05 * math.sin(2 * math.pi * h / 72), 2),
        nitrogen=round(SOIL_PARAMS[i][3] - 0.1 * h, 1),  # 作物吸收导致缓慢下降
        phosphorus=round(45 + 6 * math.cos(i * 0.7) + 0.5 * math.sin(h / 24), 1),
        potassium=round(185 + 20 * math.sin(i * 0.9) + 1.5 * math.cos(h / 24), 1),
        conductivity=round(1.2 + 0.2 * math.sin(i + h / 50), 2),
    )


def seed_smart_agriculture(db: Session) -> bool:
    """写入默认数据；有新数据写入时返回 True"""
    changed = False
    if db.query(EnvironmentReading).first() is None and db.query(IrrigationZone).first() is None:
        _seed_sensors_and_irrigation(db)
        changed = True
    # 数字营销默认数据（main.py 未直接调用，故在此调用）
    if seed_digital_marketing(db):
        changed = True
    return changed


def _seed_sensors_and_irrigation(db: Session) -> None:
    end = datetime.now().replace(minute=0, second=0, microsecond=0)
    t0 = end - timedelta(hours=HOURS - 1)
    stations = _stations(db)

    zones = []
    for i, (land_id, _) in enumerate(stations):
        name, flow, pressure, duration, auto = ZONES[i]
        zone = IrrigationZone(
            name=name, land_id=land_id, status="停止", auto_mode=auto,
            rated_flow=flow, pressure=pressure, planned_duration=0, updated_at=end,
        )
        db.add(zone)
        zones.append(zone)
    db.flush()

    for i, (land_id, location) in enumerate(stations):
        zone = zones[i]
        _, flow, _, duration, auto = ZONES[i]
        last_irr = -(20 + 7 * i)  # 起始前最近一次灌溉（相对小时）
        last_value = None
        for h in range(HOURS):
            if _is_irrigation_hour(t0, h, i):
                ts = t0 + timedelta(hours=h)
                before = last_value if last_value is not None else _moisture(i, h - last_irr, 0)
                last_irr = h
                reading = _reading(t0, h, i, land_id, location, 0)
                db.add(IrrigationRecord(
                    zone_id=zone.id, land_id=land_id, mode="auto" if auto else "manual",
                    started_at=ts, ended_at=ts + timedelta(minutes=duration), duration=duration,
                    water_volume=round(flow * duration / 60, 2),
                    moisture_before=round(before, 1), moisture_after=reading.soil_moisture,
                ))
            else:
                reading = _reading(t0, h, i, land_id, location, h - last_irr)
            db.add(reading)
            last_value = reading.soil_moisture

        if i in RUNNING_ZONES:
            # 当前正在进行的一次灌溉：开始于最新一次采集时刻，尚未结束
            zone.status = "运行中"
            zone.planned_duration = duration
            zone.started_at = end
            db.add(IrrigationRecord(
                zone_id=zone.id, land_id=land_id, mode="auto" if auto else "manual",
                started_at=end, ended_at=None, duration=0, water_volume=0,
                moisture_before=last_value, moisture_after=None,
            ))
    db.commit()
