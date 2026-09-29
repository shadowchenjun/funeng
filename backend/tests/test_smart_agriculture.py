"""智慧农业：传感器 / 灌溉 / 分析接口均来自数据库"""
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.smart_agriculture import EnvironmentReading, IrrigationRecord, IrrigationZone, Land

BASE = "/api/smart-agriculture"


def _get(client, headers, path):
    resp = client.get(f"{BASE}{path}", headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_requires_login(client):
    assert client.get(f"{BASE}/soil").status_code == 401


def test_sensor_endpoints_are_stable(client, user_headers):
    for path in ("/soil", "/weather", "/irrigation", "/analytics", "/monitor", "/readings?hours=24"):
        first = _get(client, user_headers, path)
        second = _get(client, user_headers, path)
        assert first == second, path
        assert first, path


def test_soil_and_weather_match_latest_readings(client, user_headers):
    soil = _get(client, user_headers, "/soil")
    weather = _get(client, user_headers, "/weather")
    assert len(soil) == len(weather) == 4
    expected_keys = {"id", "sensor_id", "location", "temperature", "humidity", "ph", "nitrogen",
                     "phosphorus", "potassium", "conductivity", "timestamp"}
    assert expected_keys <= set(soil[0])
    assert {"wind_speed", "wind_direction", "precipitation", "atmospheric_pressure", "uv_index",
            "visibility"} <= set(weather[0])
    with SessionLocal() as db:
        for item in soil:
            row = db.query(EnvironmentReading).filter(EnvironmentReading.sensor_id == item["sensor_id"]) \
                .order_by(EnvironmentReading.recorded_at.desc()).first()
            assert row.recorded_at.isoformat() == item["timestamp"]
            assert row.soil_moisture == item["humidity"]
            assert row.soil_ph == item["ph"]
        # 种子数据为 7 天逐小时
        assert db.query(EnvironmentReading).filter(EnvironmentReading.sensor_id == "S001").count() == 7 * 24


def test_readings_series(client, user_headers):
    series = _get(client, user_headers, "/readings?sensor_id=S001&hours=24")
    assert len(series) == 24
    stamps = [r["timestamp"] for r in series]
    assert stamps == sorted(stamps)


def test_monitor_is_average_of_latest(client, user_headers):
    monitor = _get(client, user_headers, "/monitor")
    weather = _get(client, user_headers, "/weather")
    soil = _get(client, user_headers, "/soil")
    assert monitor["stationCount"] == 4
    assert monitor["temperature"] == round(sum(w["temperature"] for w in weather) / 4, 1)
    assert monitor["soilMoisture"] == round(sum(s["humidity"] for s in soil) / 4, 1)


def test_analytics_consistent_with_rows(client, user_headers):
    data = _get(client, user_headers, "/analytics")
    assert set(data) == {"soil_health", "water_usage", "crop_status", "yield_prediction"}
    assert 0 <= data["soil_health"]["score"] <= 100
    with SessionLocal() as db:
        lands = db.query(Land).all()
        assert data["crop_status"]["total_area"] == round(sum(l.area or 0 for l in lands), 1)
        day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week = db.query(IrrigationRecord).filter(
            IrrigationRecord.started_at >= day - timedelta(days=7), IrrigationRecord.started_at < day
        ).all()
    assert data["water_usage"]["week_avg"] == round(sum(r.water_volume for r in week) / 7, 1)
    assert data["crop_status"]["healthy"] + data["crop_status"]["warning"] + data["crop_status"]["critical"] in (99, 100, 101)


def test_irrigation_control_persists(client, user_headers):
    zones = _get(client, user_headers, "/irrigation")
    stopped = next(z for z in zones if z["status"] == "停止")
    zid = stopped["id"]
    with SessionLocal() as db:
        before = db.query(IrrigationRecord).filter(IrrigationRecord.zone_id == zid).count()

    resp = client.post(f"{BASE}/irrigation/{zid}/control", json={"action": "start", "duration": 30},
                       headers=user_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "运行中"
    assert resp.json()["duration"] == 30
    # 重复启动应被拒绝
    assert client.post(f"{BASE}/irrigation/{zid}/control", json={"action": "start"},
                       headers=user_headers).status_code == 400

    zone = next(z for z in _get(client, user_headers, "/irrigation") if z["id"] == zid)
    assert zone["status"] == "运行中"
    assert zone["water_flow"] > 0

    resp = client.post(f"{BASE}/irrigation/{zid}/control", json={"action": "stop"}, headers=user_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "停止"
    with SessionLocal() as db:
        records = db.query(IrrigationRecord).filter(IrrigationRecord.zone_id == zid) \
            .order_by(IrrigationRecord.id.desc()).all()
        assert len(records) == before + 1
        assert records[0].mode == "manual"
        assert records[0].ended_at is not None
        assert db.get(IrrigationZone, zid).status == "停止"

    assert client.post(f"{BASE}/irrigation/{zid}/control", json={"action": "bogus"},
                       headers=user_headers).status_code == 400
    assert client.post(f"{BASE}/irrigation/99999/control", json={"action": "start"},
                       headers=user_headers).status_code == 404
