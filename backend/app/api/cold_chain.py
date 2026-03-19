"""
数字冷链物联API
"""
import sqlite3
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random

router = APIRouter()

def get_db():
    import os
    # 使用相对路径，与其他模块保持一致
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'funeng.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 冷链运输数据模型
class TransportData(BaseModel):
    id: str
    vehicle_no: str  # 车牌号
    driver: str
    route: str
    status: str  # 运输中/到达/等待
    temperature: float
    humidity: float
    location: str
    eta: str

# 仓储数据模型
class WarehouseData(BaseModel):
    id: str
    name: str
    capacity: float  # 容量 吨
    used: float  # 已用
    temperature: float
    humidity: float
    products: list

# 温度告警模型
class TemperatureAlert(BaseModel):
    id: str
    sensor_id: str
    location: str
    temperature: float
    threshold: float
    severity: str  # warning/critical
    timestamp: str

@router.get("/transport")
def get_transports():
    """获取运输列表"""
    vehicles = ["京A12345", "京B67890", "津C11111", "冀D22222", "鲁E33333"]
    drivers = ["张师傅", "李师傅", "王师傅", "刘师傅", "陈师傅"]
    routes = ["北京-上海", "广州-成都", "武汉-西安", "杭州-重庆", "深圳-北京"]
    statuses = ["运输中", "运输中", "运输中", "到达", "等待"]
    
    transports = []
    for i in range(15):
        transports.append({
            "id": f"T{i+1:04d}",
            "vehicle_no": random.choice(vehicles),
            "driver": random.choice(drivers),
            "route": random.choice(routes),
            "status": random.choice(statuses),
            "temperature": round(random.uniform(-5, 8), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "location": random.choice(["北京", "上海", "广州", "成都", "武汉", "西安", "杭州", "重庆", "深圳"]),
            "speed": round(random.uniform(0, 120), 0),
            "fuel": round(random.uniform(20, 100), 0),
            "eta": (datetime.now() + timedelta(hours=random.randint(1, 24))).strftime("%Y-%m-%d %H:%M"),
            "departure_time": (datetime.now() - timedelta(hours=random.randint(2, 48))).strftime("%Y-%m-%d %H:%M"),
            "cargo": random.choice(["新鲜蔬菜", "水果", "肉类", "冷冻食品", "乳制品"]),
            "weight": round(random.uniform(5, 30), 1)
        })
    return transports

@router.get("/transport/{transport_id}")
def get_transport_detail(transport_id: str):
    """获取运输详情"""
    return {
        "id": transport_id,
        "vehicle_no": "京A12345",
        "driver": "张师傅",
        "driver_phone": "138****1234",
        "route": "北京-上海",
        "status": "运输中",
        "temperature": round(random.uniform(-5, 8), 1),
        "humidity": round(random.uniform(40, 80), 1),
        "current_location": "天津",
        "speed": round(random.uniform(60, 100), 0),
        "fuel": round(random.uniform(30, 80), 0),
        "eta": (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
        "departure_time": (datetime.now() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M"),
        "cargo": "新鲜蔬菜",
        "weight": round(random.uniform(10, 25), 1),
        "route_points": [
            {"location": "北京", "time": "08:00", "status": "已离开"},
            {"location": "天津", "time": "10:30", "status": "已通过"},
            {"location": "济南", "time": "14:00", "status": "预计"},
            {"location": "南京", "time": "20:00", "status": "预计"},
            {"location": "上海", "time": "24:00", "status": "预计"}
        ],
        "temperature_history": [
            {"time": "08:00", "temp": 2.5},
            {"time": "10:00", "temp": 2.8},
            {"time": "12:00", "temp": 3.1},
            {"time": "14:00", "temp": 2.9},
            {"time": "16:00", "temp": 3.0}
        ]
    }

@router.get("/warehouse")
def get_warehouses():
    """获取仓储列表"""
    warehouses = []
    for i in range(8):
        capacity = random.randint(500, 2000)
        used = random.randint(100, int(capacity * 0.9))
        
        warehouses.append({
            "id": f"W{i+1:02d}",
            "name": f"{random.choice(['北京', '上海', '广州', '成都', '武汉'])}中心仓库{i+1}",
            "address": f"{random.choice(['北京', '上海', '广州', '成都', '武汉'])}市{random.choice(['朝阳', '海淀', '浦东', '天河'])}区",
            "capacity": capacity,
            "used": used,
            "available": capacity - used,
            "utilization": round(used / capacity * 100, 1),
            "temperature": round(random.uniform(-5, 10), 1),
            "humidity": round(random.uniform(40, 70), 1),
            "products_count": random.randint(10, 100),
            "alerts": random.randint(0, 5)
        })
    return warehouses

@router.get("/warehouse/{warehouse_id}")
def get_warehouse_detail(warehouse_id: str):
    """获取仓储详情"""
    return {
        "id": warehouse_id,
        "name": "北京中心仓库1",
        "address": "北京市朝阳区",
        "capacity": 1000,
        "used": 650,
        "available": 350,
        "temperature": round(random.uniform(0, 8), 1),
        "humidity": round(random.uniform(45, 65), 1),
        "zones": [
            {"name": "冷冻区", "temp_range": "-18~-25", "capacity": 300, "used": 250},
            {"name": "冷藏区", "temp_range": "0~5", "capacity": 400, "used": 280},
            {"name": "常温区", "temp_range": "10~25", "capacity": 300, "used": 120}
        ],
        "products": [
            {"name": "有机蔬菜", "quantity": 150, "zone": "冷藏区", "shelf_date": "2026-02-10"},
            {"name": "新鲜水果", "quantity": 200, "zone": "冷藏区", "shelf_date": "2026-02-15"},
            {"name": "冷冻肉类", "quantity": 250, "zone": "冷冻区", "shelf_date": "2026-01-20"}
        ]
    }

@router.get("/monitoring/temperature")
def get_temperature_monitoring():
    """获取温度监控数据"""
    locations = ["冷藏车1号", "冷藏车2号", "冷库1号", "冷库2号", "冷库3号"]
    
    data = []
    for i, location in enumerate(locations):
        base_temp = random.uniform(-20, 5)
        data.append({
            "id": i + 1,
            "location": location,
            "current_temp": round(base_temp, 1),
            "target_temp": round(random.uniform(-20, 5), 1),
            "min_temp": round(base_temp - random.uniform(1, 3), 1),
            "max_temp": round(base_temp + random.uniform(1, 3), 1),
            "humidity": round(random.uniform(40, 80), 1),
            "status": "正常" if abs(base_temp - random.uniform(-20, 5)) < 3 else "告警",
            "last_update": datetime.now().isoformat()
        })
    return data

@router.get("/monitoring/alerts")
def get_alerts():
    """获取温度告警列表"""
    alerts = []
    severity_list = ["warning", "critical"]
    locations = ["冷藏车1号", "冷库2号", "冷藏车3号", "冷库1号"]
    
    for i in range(10):
        severity = random.choice(severity_list)
        alerts.append({
            "id": f"A{i+1:04d}",
            "sensor_id": f"SEN{random.randint(100, 999)}",
            "location": random.choice(locations),
            "type": "温度异常",
            "temperature": round(random.uniform(-10, 15), 1),
            "threshold": round(random.uniform(-5, 10), 1),
            "severity": severity,
            "status": random.choice(["未处理", "处理中", "已解决"]),
            "message": "温度超过阈值" if severity == "warning" else "温度严重超标",
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat()
        })
    return alerts

@router.get("/traceability")
def get_traceability():
    """获取质量追溯数据"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM traceability_records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    batches = []
    for row in rows:
        batches.append({
            "batch_no": row["product_batch"],
            "product": row["product_name"],
            "source": row["origin_farm"],
            "production_date": row["harvest_date"] or row["planting_date"],
            "harvest_time": row["harvest_date"],
            "warehouse_in": row["processing_date"],
            "warehouse_out": row["sale_date"],
            "transport_id": row["logistics_no"],
            "retailer": row["retail_outlet"],
            "status": row["status"],
            "quality_check": {
                "passed": row["inspection_report"] is not None,
                "temperature": random.uniform(0, 8),
                "humidity": random.uniform(40, 70),
                "inspector": "质检员A",
                "result": "合格" if row["inspection_report"] else "待检"
            }
        })
    return batches

@router.get("/traceability/{batch_no}")
def get_batch_detail(batch_no: str):
    """获取批次追溯详情"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM traceability_records WHERE product_batch = ?", (batch_no,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {
            "batch_no": batch_no,
            "product": "有机蔬菜",
            "source": "基地A",
            "production_date": "2026-02-01",
            "trace_data": [
                {"stage": "种植", "location": "基地A", "time": "2026-02-01 08:00", "detail": "播种完成", "operator": "农技师张三"},
                {"stage": "采收", "location": "基地A", "time": "2026-02-10 06:00", "detail": "采收完成", "operator": "农户李四"},
                {"stage": "初加工", "location": "基地A加工中心", "time": "2026-02-10 10:00", "detail": "清洗包装", "operator": "工人王五"},
                {"stage": "入库", "location": "北京中心仓库", "time": "2026-02-10 18:00", "detail": "温度2°C入库", "operator": "仓管赵六"},
                {"stage": "出库", "location": "北京中心仓库", "time": "2026-02-12 08:00", "detail": "装车运输", "operator": "司机张师傅"},
                {"stage": "配送", "location": "门店1", "time": "2026-02-12 14:00", "detail": "已送达", "operator": "配送员钱七"}
            ]
        }
    
    return {
        "batch_no": row["product_batch"],
        "product": row["product_name"],
        "source": row["origin_farm"],
        "production_date": row["harvest_date"] or row["planting_date"],
        "origin_address": row["origin_address"],
        "planting_date": row["planting_date"],
        "harvest_date": row["harvest_date"],
        "processing_date": row["processing_date"],
        "processing_factory": row["processing_factory"],
        "logistics_company": row["logistics_company"],
        "logistics_no": row["logistics_no"],
        "warehouse": row["warehouse"],
        "retail_outlet": row["retail_outlet"],
        "sale_date": row["sale_date"],
        "certifications": row["certifications"],
        "inspection_report": row["inspection_report"],
        "trace_code": row["trace_code"],
        "status": row["status"],
        "trace_data": [
            {"stage": "种植", "location": row["origin_address"], "time": f"{row['planting_date']} 08:00" if row["planting_date"] else "未知", "detail": "播种/定植", "operator": "基地管理员"},
            {"stage": "采收", "location": row["origin_farm"], "time": f"{row['harvest_date']} 06:00" if row["harvest_date"] else "未知", "detail": "采收完成", "operator": "采收工人"},
            {"stage": "加工", "location": row["processing_factory"] or "无", "time": f"{row['processing_date']} 10:00" if row["processing_date"] else "无", "detail": "加工包装", "operator": "加工人员"},
            {"stage": "入库", "location": row["warehouse"] or "无", "time": f"{row['processing_date']} 18:00" if row["processing_date"] else "无", "detail": "入库存储", "operator": "仓管人员"},
            {"stage": "出库", "location": row["warehouse"] or "无", "time": f"{row['sale_date']} 08:00" if row["sale_date"] else "无", "detail": "装车运输", "operator": "物流司机"},
            {"stage": "配送", "location": row["retail_outlet"] or "无", "time": f"{row['sale_date']} 14:00" if row["sale_date"] else "无", "detail": "已送达门店", "operator": "配送员"}
        ]
    }

@router.get("/analytics")
def get_cold_chain_analytics():
    """获取冷链分析数据"""
    return {
        "transport": {
            "total_vehicles": random.randint(20, 50),
            "active": random.randint(15, 40),
            "on_time_rate": round(random.uniform(85, 99), 1),
            "avg_temp_compliance": round(random.uniform(95, 99.5), 1)
        },
        "warehouse": {
            "total_capacity": random.randint(5000, 10000),
            "utilization": round(random.uniform(60, 85), 1),
            "avg_temp_stability": round(random.uniform(95, 99), 1)
        },
        "quality": {
            "total_batches": random.randint(500, 2000),
            "pass_rate": round(random.uniform(95, 99.5), 1),
            "complaints": random.randint(0, 20),
            "claims": random.randint(0, 10)
        },
        "cost": {
            "electricity": round(random.uniform(50000, 150000), 2),
            "fuel": round(random.uniform(30000, 80000), 2),
            "maintenance": round(random.uniform(10000, 30000), 2)
        }
    }

# ========== 品控管理 ==========
@router.get("/quality/inspections")
def get_quality_inspections():
    """获取品控检查记录列表"""
    inspection_types = ["入库检查", "出库检查", "在库检查", "运输检查", "终端检查"]
    results = ["合格", "待复检", "不合格"]
    products = ["有机蔬菜", "新鲜水果", "土特产", "冷冻肉类", "乳制品"]
    
    inspections = []
    for i in range(20):
        inspection_id = f"QC{i+1:05d}"
        insp_type = random.choice(inspection_types)
        result = random.choice(results)
        
        inspections.append({
            "id": inspection_id,
            "type": insp_type,
            "product": random.choice(products),
            "batch_no": f"BATCH{datetime.now().strftime('%Y%m')}{random.randint(1, 999):04d}",
            "quantity": round(random.uniform(10, 500), 1),
            "result": result,
            "score": round(random.uniform(60, 100), 1) if result == "合格" else round(random.uniform(40, 70), 1),
            "temperature": round(random.uniform(-5, 10), 1),
            "humidity": round(random.uniform(35, 75), 1),
            "pesticide_residue": round(random.uniform(0, 0.5), 3),
            "heavy_metal": round(random.uniform(0, 0.1), 3),
            "inspector": f"质检员{random.randint(1, 10)}",
            "location": random.choice(["北京中心仓库", "上海中心仓库", "广州中心仓库", "成都中心仓库"]),
            "remark": "无异常" if result == "合格" else random.choice(["温度超标", "农药残留超标", "包装损坏", "需要复检"]),
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 168))).strftime("%Y-%m-%d %H:%M")
        })
    return inspections

@router.get("/quality/inspections/{inspection_id}")
def get_quality_inspection_detail(inspection_id: str):
    """获取品控检查详情"""
    return {
        "id": inspection_id,
        "type": "入库检查",
        "product": "有机蔬菜",
        "batch_no": "QC20260200001",
        "quantity": 150.5,
        "result": "合格",
        "score": 92.5,
        "temperature": 3.2,
        "humidity": 65.0,
        "pesticide_residue": 0.12,
        "heavy_metal": 0.02,
        "inspector": "质检员张三",
        "location": "北京中心仓库",
        "remark": "无异常",
        "items": [
            {"name": "外观检查", "result": "合格", "score": 95},
            {"name": "色泽检查", "result": "合格", "score": 90},
            {"name": "气味检查", "result": "合格", "score": 92},
            {"name": "温度检测", "result": "合格", "score": 88},
            {"name": "农残检测", "result": "合格", "score": 98},
            {"name": "重金属检测", "result": "合格", "score": 96}
        ],
        "images": [
            "https://via.placeholder.com/200x150?text=sample1",
            "https://via.placeholder.com/200x150?text=sample2"
        ],
        "created_at": (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    }

@router.post("/quality/inspections")
def create_quality_inspection(data: dict):
    """创建品控检查记录"""
    return {
        "success": True,
        "id": f"QC{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}",
        "message": "品控检查记录创建成功"
    }

@router.get("/quality/standards")
def get_quality_standards():
    """获取品控标准"""
    return {
        "standards": [
            {
                "id": "QS001",
                "name": "新鲜蔬菜品控标准",
                "category": "蔬菜",
                "temperature": {"min": 0, "max": 8, "unit": "°C"},
                "humidity": {"min": 85, "max": 95, "unit": "%"},
                "pesticide_residue_max": 0.5,
                "heavy_metal_max": 0.1,
                "shelf_days": 7
            },
            {
                "id": "QS002",
                "name": "水果品控标准",
                "category": "水果",
                "temperature": {"min": 0, "max": 12, "unit": "°C"},
                "humidity": {"min": 80, "max": 90, "unit": "%"},
                "pesticide_residue_max": 0.3,
                "heavy_metal_max": 0.05,
                "shelf_days": 14
            },
            {
                "id": "QS003",
                "name": "冷冻食品品控标准",
                "category": "冷冻食品",
                "temperature": {"min": -25, "max": -18, "unit": "°C"},
                "humidity": {"min": 70, "max": 85, "unit": "%"},
                "pesticide_residue_max": 0.1,
                "heavy_metal_max": 0.02,
                "shelf_days": 180
            },
            {
                "id": "QS004",
                "name": "肉类品控标准",
                "category": "肉类",
                "temperature": {"min": -2, "max": 4, "unit": "°C"},
                "humidity": {"min": 75, "max": 85, "unit": "%"},
                "pesticide_residue_max": 0.2,
                "heavy_metal_max": 0.05,
                "shelf_days": 5
            }
        ]
    }

# ========== 库存预警 ==========
@router.get("/inventory/alerts")
def get_inventory_alerts():
    """获取库存预警列表"""
    alert_types = ["库存不足", "库存过多", "临期预警", "温度异常", "湿度异常"]
    alert_levels = ["low", "medium", "high", "critical"]
    products = ["有机蔬菜", "新鲜水果", "土特产", "冷冻肉类", "乳制品"]
    warehouses = ["北京中心仓库1", "上海中心仓库", "广州中心仓库", "成都中心仓库"]
    
    alerts = []
    for i in range(25):
        alert_type = random.choice(alert_types)
        level = random.choice(alert_levels)
        
        # 根据类型生成相关数据
        if alert_type == "库存不足":
            current = random.randint(0, 50)
            min_stock = random.randint(80, 200)
            status = "待处理"
        elif alert_type == "库存过多":
            current = random.randint(800, 1500)
            max_stock = random.randint(500, 800)
            status = random.choice(["待处理", "已确认"])
        elif alert_type == "临期预警":
            days_left = random.randint(1, 15)
            current = random.randint(50, 200)
            status = random.choice(["待处理", "处理中"])
        elif alert_type == "温度异常":
            current = round(random.uniform(-10, 15), 1)
            target = round(random.uniform(-5, 5), 1)
            status = random.choice(["待处理", "处理中", "已解决"])
        else:
            current = round(random.uniform(20, 95), 1)
            target = round(random.uniform(40, 70), 1)
            status = random.choice(["待处理", "已解决"])
        
        alerts.append({
            "id": f"IA{i+1:04d}",
            "type": alert_type,
            "level": level,
            "product": random.choice(products),
            "warehouse": random.choice(warehouses),
            "current_value": current,
            "threshold": min_stock if alert_type == "库存不足" else (max_stock if alert_type == "库存过多" else (days_left if alert_type == "临期预警" else target)),
            "unit": "件" if alert_type in ["库存不足", "库存过多"] else ("天" if alert_type == "临期预警" else "°C" if "温度" in alert_type else "%"),
            "status": status,
            "message": get_alert_message(alert_type, current),
            "created_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M")
        })
    
    # 按级别排序
    level_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda x: level_order.get(x["level"], 4))
    return alerts

def get_alert_message(alert_type: str, current: float) -> str:
    """生成预警消息"""
    messages = {
        "库存不足": f"当前库存{current:.0f}件，低于安全库存",
        "库存过多": f"当前库存{current:.0f}件，超过最大库存",
        "临期预警": f"还有{int(current)}天到期，请及时处理",
        "温度异常": f"当前温度{current}°C，超出正常范围",
        "湿度异常": f"当前湿度{current}%，超出正常范围"
    }
    return messages.get(alert_type, "")

@router.get("/inventory/alerts/{alert_id}")
def get_inventory_alert_detail(alert_id: str):
    """获取库存预警详情"""
    return {
        "id": alert_id,
        "type": "库存不足",
        "level": "high",
        "product": "有机蔬菜",
        "product_code": "SKU001",
        "warehouse": "北京中心仓库1",
        "zone": "冷藏区A",
        "current_stock": 45,
        "min_stock": 150,
        "max_stock": 800,
        "unit": "件",
        "history": [
            {"date": "2026-02-15", "stock": 180},
            {"date": "2026-02-16", "stock": 120},
            {"date": "2026-02-17", "stock": 80},
            {"date": "2026-02-18", "stock": 45}
        ],
        "suggestions": [
            "建议立即补货",
            "检查供应链是否有延迟",
            "考虑增加安全库存量"
        ],
        "status": "待处理",
        "created_at": "2026-02-18 10:30:00",
        "updated_at": "2026-02-18 11:00:00"
    }

@router.post("/inventory/alerts/{alert_id}/resolve")
def resolve_inventory_alert(alert_id: str, data: dict = {}):
    """处理库存预警"""
    return {
        "success": True,
        "message": f"预警 {alert_id} 已标记为已处理"
    }

@router.get("/inventory/rules")
def get_inventory_rules():
    """获取库存预警规则"""
    return {
        "rules": [
            {
                "id": "RULE001",
                "name": "安全库存预警",
                "type": "库存不足",
                "enabled": True,
                "threshold": 150,
                "unit": "件",
                "product_categories": ["蔬菜", "水果", "肉类"],
                "notify_channels": ["短信", "邮件", "APP"]
            },
            {
                "id": "RULE002",
                "name": "临期预警",
                "type": "临期预警",
                "enabled": True,
                "threshold": 7,
                "unit": "天",
                "product_categories": ["全部"],
                "notify_channels": ["短信", "APP"]
            },
            {
                "id": "RULE003",
                "name": "库容预警",
                "type": "库存过多",
                "enabled": True,
                "threshold": 90,
                "unit": "%",
                "product_categories": ["全部"],
                "notify_channels": ["邮件"]
            },
            {
                "id": "RULE004",
                "name": "温度监控预警",
                "type": "温度异常",
                "enabled": True,
                "threshold": 5,
                "unit": "°C",
                "product_categories": ["冷冻食品", "冷藏品"],
                "notify_channels": ["短信", "邮件", "APP", "电话"]
            }
        ]
    }

@router.post("/inventory/rules")
def create_inventory_rule(data: dict):
    """创建库存预警规则"""
    return {
        "success": True,
        "id": f"RULE{datetime.now().strftime('%Y%m%d')}{random.randint(100, 999)}",
        "message": "预警规则创建成功"
    }

@router.get("/inventory/stats")
def get_inventory_stats():
    """获取库存统计概览"""
    return {
        "total_products": random.randint(500, 1500),
        "total_stock": random.randint(50000, 100000),
        "low_stock_count": random.randint(5, 20),
        "overstock_count": random.randint(3, 15),
        "expiring_soon_count": random.randint(10, 30),
        "temp_alert_count": random.randint(0, 5),
        "today_resolved": random.randint(5, 15),
        "this_week": {
            "total_alerts": random.randint(30, 80),
            "resolved": random.randint(25, 70),
            "pending": random.randint(5, 20)
        }
    }


# ========== 货主管理 ==========
@router.get("/owner/list")
def get_owner_list():
    """获取货主列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cargo_owners ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    
    owners = []
    for row in rows:
        owners.append({
            "id": row["id"],
            "code": row["code"],
            "name": row["name"],
            "contact": row["contact"],
            "phone": row["phone"],
            "email": row["email"],
            "address": row["address"],
            "status": row["status"],
            "created_at": row["created_at"],
            "warehouse_count": random.randint(1, 5),
            "zone_count": random.randint(2, 10),
            "total_stock": random.randint(1000, 50000)
        })
    return owners

@router.get("/owner/{owner_id}")
def get_owner_detail(owner_id: int):
    """获取货主详情"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cargo_owners WHERE id = ?", (owner_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": "货主不存在"}
    
    return {
        "id": row["id"],
        "code": row["code"],
        "name": row["name"],
        "contact": row["contact"],
        "phone": row["phone"],
        "email": row["email"],
        "address": row["address"],
        "status": row["status"],
        "warehouses": [
            {"id": "WH001", "name": "北京中心仓", "zones": 5},
            {"id": "WH002", "name": "上海中心仓", "zones": 3}
        ],
        "pricing_model": "按件计费+固定月租",
        "contracts": [
            {"no": "CT202601001", "start": "2026-01-01", "end": "2026-12-31", "status": "生效中"}
        ]
    }

@router.post("/owner")
def create_owner(data: dict):
    """创建货主"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 生成货主编码
    cursor.execute("SELECT MAX(id) as max_id FROM cargo_owners")
    result = cursor.fetchone()
    new_id = (result["max_id"] or 0) + 1
    code = f"OW{1000 + new_id}"
    
    cursor.execute("""
        INSERT INTO cargo_owners (code, name, contact, phone, email, address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (code, data.get("name"), data.get("contact"), data.get("phone"), 
          data.get("email"), data.get("address"), data.get("status", "正常")))
    conn.commit()
    new_owner_id = cursor.lastrowid
    conn.close()
    
    return {"success": True, "id": new_owner_id, "code": code}

@router.put("/owner/{owner_id}")
def update_owner(owner_id: int, data: dict):
    """更新货主信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE cargo_owners 
        SET name = ?, contact = ?, phone = ?, email = ?, address = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (data.get("name"), data.get("contact"), data.get("phone"), 
          data.get("email"), data.get("address"), data.get("status"), owner_id))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": f"货主 {owner_id} 更新成功"}

@router.delete("/owner/{owner_id}")
def delete_owner(owner_id: int):
    """删除货主"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cargo_owners WHERE id = ?", (owner_id,))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": f"货主 {owner_id} 删除成功"}


# ========== 温区管理 ==========
@router.get("/zone/list")
def get_zone_list():
    """获取温区列表"""
    zones = []
    zone_types = ["冷藏区", "冷冻区", "常温区", "恒温区"]
    for i in range(20):
        zones.append({
            "id": f"Z{i+1:04d}",
            "name": f"{zone_types[i%4]}{chr(65+i//4)}",
            "type": zone_types[i%4],
            "temperature_min": random.choice([-18, 0, 5, 15]),
            "temperature_max": random.choice([-12, 5, 10, 25]),
            "warehouse": f"仓库{random.randint(1, 5)}",
            "capacity": random.randint(100, 1000),
            "used": random.randint(10, 500),
            "status": random.choice(["正常", "正常", "维护中"])
        })
    return zones


# ========== 入库管理 ==========
@router.get("/inbound/appointments")
def get_inbound_appointments():
    """获取入库预约列表"""
    appointments = []
    for i in range(15):
        appt_id = f"INB{datetime.now().strftime('%Y%m')}{i+1:04d}"
        appointments.append({
            "id": appt_id,
            "owner": f"货主{random.randint(1, 15)}",
            "owner_code": f"OW{1000+random.randint(0, 14)}",
            "vehicle_no": f"京A{random.randint(10000, 99999)}",
            "driver": f"司机{random.randint(1, 10)}",
            "driver_phone": f"138{random.randint(10000000, 99999999)}",
            "estimated_arrival": (datetime.now() + timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M"),
            "actual_arrival": None,
            "appointment_date": (datetime.now() + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d"),
            "expected_items": random.randint(5, 50),
            "expected_quantity": random.randint(100, 5000),
            "status": random.choice(["已预约", "已到货", "收货中", "已完成"]),
            "dock": f"D{random.randint(1, 10)}",
            "zone": random.choice(["冷藏区", "冷冻区", "常温区"]),
            "remark": random.choice(["", "加急", "需要叉车", "散货"])
        })
    return appointments

@router.get("/inbound/appointments/{appointment_id}")
def get_appointment_detail(appointment_id: str):
    """获取预约详情"""
    return {
        "id": appointment_id,
        "owner": "货主A",
        "owner_code": "OW1000",
        "vehicle_no": "京A12345",
        "driver": "司机张三",
        "driver_phone": "13812345678",
        "estimated_arrival": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "appointment_date": datetime.now().strftime("%Y-%m-%d"),
        "expected_items": 20,
        "expected_quantity": 2000,
        "items": [
            {"sku": "SKU001", "name": "有机蔬菜", "quantity": 500, "unit": "件", "barcode": "6901234567890"},
            {"sku": "SKU002", "name": "新鲜水果", "quantity": 300, "unit": "件", "barcode": "6901234567891"},
            {"sku": "SKU003", "name": "冷冻肉类", "quantity": 200, "unit": "件", "barcode": "6901234567892"}
        ],
        "status": "已到货",
        "dock": "D1",
        "zone": "冷藏区A"
    }

@router.post("/inbound/appointments")
def create_appointment(data: dict):
    """创建入库预约"""
    return {"success": True, "id": f"INB{datetime.now().strftime('%Y%m%d')}{random.randint(100, 999)}"}

@router.put("/inbound/appointments/{appointment_id}/checkin")
def checkin_appointment(appointment_id: str):
    """签到确认到货"""
    return {"success": True, "message": f"预约 {appointment_id} 已签到"}


# ========== 入库单 ==========
@router.get("/inbound/orders")
def get_inbound_orders():
    """获取入库单列表"""
    orders = []
    for i in range(20):
        order_id = f"IOR{datetime.now().strftime('%Y%m')}{i+1:04d}"
        orders.append({
            "id": order_id,
            "appointment_id": f"INB{datetime.now().strftime('%Y%m')}{random.randint(1,15):04d}",
            "owner": f"货主{random.randint(1, 15)}",
            "inbound_date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "status": random.choice(["待收货", "收货中", "已入库", "已质检"]),
            "total_items": random.randint(5, 50),
            "total_quantity": random.randint(100, 5000),
            "received_quantity": 0,
            "qualified_quantity": 0,
            "unqualified_quantity": 0,
            "dock": f"D{random.randint(1, 10)}",
            "receiver": f"收货员{random.randint(1, 5)}",
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M")
        })
    return orders

@router.get("/inbound/orders/{order_id}")
def get_inbound_order_detail(order_id: str):
    """获取入库单详情"""
    return {
        "id": order_id,
        "appointment_id": "INB2026020001",
        "owner": "货主A",
        "inbound_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "收货中",
        "total_items": 20,
        "total_quantity": 2000,
        "received_quantity": 1500,
        "qualified_quantity": 1450,
        "unqualified_quantity": 50,
        "dock": "D1",
        "receiver": "收货员张三",
        "items": [
            {"sku": "SKU001", "name": "有机蔬菜", "expected": 500, "received": 480, "qualified": 475, "unqualified": 5, "location": "A01-01-01"},
            {"sku": "SKU002", "name": "新鲜水果", "expected": 300, "received": 300, "qualified": 295, "unqualified": 5, "location": "A01-01-02"},
            {"sku": "SKU003", "name": "冷冻肉类", "expected": 200, "received": 200, "qualified": 200, "unqualified": 0, "location": "B02-03-05"}
        ],
        "quality_check": {"status": "已完成", "passed": True, "score": 92}
    }


# ========== 上架建议 ==========
@router.get("/inbound/suggestions/{order_id}")
def get_putaway_suggestions(order_id: str):
    """获取智能上架建议"""
    suggestions = []
    zones = ["冷藏区A", "冷藏区B", "冷冻区A", "常温区A"]
    for i in range(10):
        suggestions.append({
            "sku": f"SKU{str(i+1).zfill(3)}",
            "name": f"商品{i+1}",
            "quantity": random.randint(50, 200),
            "suggested_location": f"{chr(65+i//10)}{i%10+1:02d}-{random.randint(1,20):02d}-{random.randint(1,30):02d}",
            "zone": random.choice(zones),
            "reason": random.choice(["温度匹配", "库存均衡", "靠近同类商品", "靠近出库口"]),
            "distance_to_pick": random.randint(5, 50),
            "confidence": round(random.uniform(0.7, 0.99), 2)
        })
    return suggestions


# ========== 作业管理 ==========
@router.get("/operation/tasks")
def get_operation_tasks():
    """获取作业任务列表"""
    tasks = []
    task_types = ["收货", "质检", "上架", "拣货", "复核", "打包", "发货", "补货", "移库", "盘点"]
    for i in range(30):
        task_id = f"TSK{i+1:05d}"
        task_type = random.choice(task_types)
        tasks.append({
            "id": task_id,
            "type": task_type,
            "priority": random.choice(["紧急", "高", "普通", "低"]),
            "status": random.choice(["待执行", "执行中", "已完成", "已取消"]),
            "owner": f"货主{random.randint(1, 10)}",
            "location": f"{chr(65+random.randint(0,5))}{random.randint(1,20):02d}-{random.randint(1,30):02d}",
            "quantity": random.randint(10, 500),
            "assigned_to": f"员工{random.randint(1, 20)}",
            "assigned_at": (datetime.now() - timedelta(hours=random.randint(0, 24))).strftime("%Y-%m-%d %H:%M"),
            "started_at": None,
            "completed_at": None,
            "barcode": f"BC{random.randint(100000, 999999)}"
        })
    return tasks

@router.get("/operation/tasks/{task_id}")
def get_task_detail(task_id: str):
    """获取作业任务详情"""
    return {
        "id": task_id,
        "type": "上架",
        "priority": "高",
        "status": "执行中",
        "owner": "货主A",
        "items": [
            {"sku": "SKU001", "name": "有机蔬菜", "barcode": "6901234567890", "quantity": 100, "location": "A01-05-10"},
            {"sku": "SKU002", "name": "新鲜水果", "barcode": "6901234567891", "quantity": 50, "location": "A01-05-11"}
        ],
        "target_location": "A01-06-15",
        "assigned_to": "员工张三",
        "assigned_at": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
        "started_at": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"),
        "history": [
            {"action": "任务分配", "operator": "系统", "time": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")},
            {"action": "开始执行", "operator": "员工张三", "time": (datetime.now() - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")},
            {"action": "扫描商品", "operator": "员工张三", "time": (datetime.now() - timedelta(minutes=25)).strftime("%Y-%m-%d %H:%M"), "detail": "SKU001 x100"}
        ]
    }

@router.post("/operation/tasks/{task_id}/start")
def start_task(task_id: str, data: dict = {}):
    """开始执行任务"""
    return {"success": True, "message": f"任务 {task_id} 开始执行", "started_at": datetime.now().strftime("%Y-%m-%d %H:%M")}

@router.post("/operation/tasks/{task_id}/complete")
def complete_task(task_id: str, data: dict = {}):
    """完成任务"""
    return {"success": True, "message": f"任务 {task_id} 已完成", "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M")}

@router.post("/operation/tasks/{task_id}/scan")
def scan_item(task_id: str, data: dict):
    """扫描条码"""
    barcode = data.get("barcode", "")
    return {"success": True, "scanned": True, "item": {"sku": "SKU001", "name": "有机蔬菜", "quantity": 100, "location": "A01-05-10"}}


# ========== 人员绩效 ==========
@router.get("/operation/performance")
def get_operator_performance():
    """获取人员绩效数据"""
    performances = []
    for i in range(20):
        performances.append({
            "employee_id": f"EMP{str(i+1).zfill(4)}",
            "name": f"员工{chr(65+i)}",
            "department": random.choice(["收货组", "上架组", "拣货组", "复核组", "发货组"]),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "tasks_completed": random.randint(10, 50),
            "tasks_handled": random.randint(10, 50),
            "error_count": random.randint(0, 5),
            "accuracy_rate": round(random.uniform(0.85, 0.99), 3),
            "avg_task_time": round(random.uniform(5, 30), 1),
            "working_hours": round(random.uniform(6, 10), 1),
            "score": random.randint(60, 100)
        })
    return performances


# ========== 智能批次调度 ==========
@router.get("/operation/batch/suggestions")
def get_batch_suggestions():
    """获取智能批次合并建议"""
    return {
        "suggestions": [
            {
                "id": "BATCH001",
                "type": "智能合并",
                "description": "将3个零散出库订单合并为一批次",
                "orders": ["OUT20260215001", "OUT20260215002", "OUT20260215003"],
                "total_items": 45,
                "estimated_pick_time": 25,
                "zone": "A区",
                "priority": "高",
                "time_window": "14:00-16:00",
                "rules_applied": ["同区域", "同配送要求", "时间窗口匹配"]
            },
            {
                "id": "BATCH002",
                "type": "顺序优化",
                "description": "优化拣货路径，预计节省30%时间",
                "orders": ["OUT20260215004", "OUT20260215005"],
                "total_items": 120,
                "estimated_pick_time": 40,
                "zone": "B区",
                "priority": "普通",
                "time_window": "10:00-12:00",
                "rules_applied": ["路径优化", "重量平衡"]
            }
        ],
        "stats": {
            "pending_orders": 15,
            "suggested_batches": 5,
            "estimated_time_saved": "35%"
        }
    }

@router.post("/operation/batch/create")
def create_batch(data: dict):
    """创建批次任务"""
    return {"success": True, "batch_id": f"BATCH{datetime.now().strftime('%Y%m%d%H%M')}", "message": "批次创建成功"}


# ========== 仓库管理（真实数据库） ==========
@router.get("/warehouses/list")
def get_warehouses_list():
    """获取仓库列表 - 从数据库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warehouses ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    warehouses = []
    for row in rows:
        warehouses.append({
            "id": row["id"],
            "name": row["name"],
            "address": row["address"],
            "capacity": row["capacity"],
            "area": row["area"],
            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "inventory": row["inventory"],
            "status": row["status"],
            "manager": row["manager"] if "manager" in row.keys() else None,
            "phone": row["phone"] if "phone" in row.keys() else None,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    return warehouses

@router.post("/warehouses")
def create_warehouse(data: dict):
    """创建仓库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO warehouses (name, address, capacity, area, temperature, humidity, inventory, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.get("name"), data.get("address"), data.get("capacity"), data.get("area"),
          data.get("temperature"), data.get("humidity"), data.get("inventory", 0), data.get("status", "正常")))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"success": True, "id": new_id, "message": "仓库创建成功"}

@router.put("/warehouses/{warehouse_id}")
def update_warehouse(warehouse_id: int, data: dict):
    """更新仓库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE warehouses
        SET name = ?, address = ?, capacity = ?, area = ?, temperature = ?, humidity = ?,
            inventory = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (data.get("name"), data.get("address"), data.get("capacity"), data.get("area"),
          data.get("temperature"), data.get("humidity"), data.get("inventory"), data.get("status"), warehouse_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "仓库更新成功"}

@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int):
    """删除仓库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM warehouses WHERE id = ?", (warehouse_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "仓库删除成功"}


# ========== 车辆管理（真实数据库） ==========
@router.get("/vehicles/list")
def get_vehicles_list():
    """获取车辆列表 - 从数据库"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    vehicles = []
    for row in rows:
        vehicles.append({
            "id": row["id"],
            "plate": row["plate"],
            "vehicleType": row["vehicle_type"] if "vehicle_type" in row.keys() else "冷藏车",
            "driver": row["driver"],
            "phone": row["phone"],
            "loadCapacity": row["load_capacity"] if "load_capacity" in row.keys() else 5,
            "volume": row["volume"] if "volume" in row.keys() else None,
            "gpsDevice": row["gps_device"] if "gps_device" in row.keys() else None,
            "tempRange": row["temp_range"] if "temp_range" in row.keys() else "-25°C~5°C",
            "status": row["status"],
            "location": row["location"],
            "temperature": row["temperature"],
            "battery": row["battery"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    return vehicles

@router.post("/vehicles")
def create_vehicle(data: dict):
    """创建车辆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vehicles (plate, vehicle_type, driver, phone, load_capacity, volume, gps_device, temp_range, status, location, temperature, battery)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.get("plate"), data.get("vehicleType", "冷藏车"), data.get("driver"), data.get("phone"),
          data.get("loadCapacity", 5), data.get("volume"), data.get("gpsDevice"), data.get("tempRange", "-25°C~5°C"),
          data.get("status", "空闲"), data.get("location", ""), data.get("temperature", -18), data.get("battery", 100)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"success": True, "id": new_id, "message": "车辆创建成功"}

@router.put("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: dict):
    """更新车辆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE vehicles
        SET plate = ?, vehicle_type = ?, driver = ?, phone = ?, load_capacity = ?,
            volume = ?, gps_device = ?, temp_range = ?, status = ?, location = ?,
            temperature = ?, battery = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (data.get("plate"), data.get("vehicleType"), data.get("driver"), data.get("phone"),
          data.get("loadCapacity"), data.get("volume"), data.get("gpsDevice"), data.get("tempRange"),
          data.get("status"), data.get("location"), data.get("temperature"), data.get("battery"), vehicle_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "车辆更新成功"}

@router.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int):
    """删除车辆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "车辆删除成功"}
