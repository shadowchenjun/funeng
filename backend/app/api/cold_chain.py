"""
数字冷链物联API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random

router = APIRouter()

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
    batches = []
    products = ["有机蔬菜", "新鲜水果", "土特产", "冷冻肉类"]
    
    for i in range(10):
        batch_id = f"BATCH{ datetime.now().strftime('%Y%m') }{i+1:04d}"
        start_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        batches.append({
            "batch_no": batch_id,
            "product": random.choice(products),
            "source": random.choice(["基地A", "基地B", "基地C", "合作社D"]),
            "production_date": start_date.strftime("%Y-%m-%d"),
            "harvest_time": start_date.strftime("%Y-%m-%d %H:%M"),
            "warehouse_in": (start_date + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "warehouse_out": (start_date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
            "transport_id": f"T{random.randint(1, 15):04d}",
            "retailer": f"门店{random.randint(1, 20)}",
            "status": random.choice(["流通中", "已售出", "已完成"]),
            "quality_check": {
                "passed": random.choice([True, True, True, False]),
                "temperature": round(random.uniform(0, 8), 1),
                "humidity": round(random.uniform(40, 70), 1),
                "inspector": f"质检员{random.randint(1, 5)}",
                "result": "合格" if True else "不合格"
            }
        })
    return batches

@router.get("/traceability/{batch_no}")
def get_batch_detail(batch_no: str):
    """获取批次追溯详情"""
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
