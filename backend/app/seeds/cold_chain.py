"""
冷链仓储默认数据（固定数据集，不使用随机数）

每张表仅在为空时写入，不会覆盖已有数据。
"""
import math
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.cold_chain import (
    CargoOwner, Vehicle, Transport,
    StorageZone, QualityInspection, InventoryRule, InventoryAlert,
    InboundAppointment, InboundOrder, InboundOrderItem, Operator, OperationTask,
    TemperatureSensor, TemperatureReading, TemperatureAlert, OperatingCost,
)
from app.models.smart_agriculture import Warehouse

T = datetime.fromisoformat

# ---------- 基础档案 ----------

# (编码, 名称, 联系人, 电话, 邮箱, 地址)
_OWNERS = [
    ("OW1001", "本来生活网", "王总", "13900139001", "wang@benlai.com", "北京市朝阳区"),
    ("OW1002", "盒马鲜生", "李总", "13900139002", "li@hema.com", "上海市浦东新区"),
    ("OW1003", "永辉超市", "赵总", "13900139003", "zhao@yonghui.com", "福建省福州市"),
    ("OW1004", "大润发", "周总", "13900139004", "zhou@rtmart.com", "江苏省南京市"),
    ("OW1005", "沃尔玛中国", "吴总", "13900139005", "wu@walmart.com", "广东省广州市"),
]

# (车牌, 司机, 电话, 载重, 容积, GPS, 状态, 位置, 温度, 电量)
_VEHICLES = [
    ("京A12345", "张师傅", "13800138001", 5, 20, "GPS001", "运输中", "京沪高速临沂段", -18, 85),
    ("京B67890", "李师傅", "13800138002", 8, 30, "GPS002", "运输中", "京港澳高速长沙段", 2.5, 92),
    ("津C11111", "王师傅", "13800138003", 5, 20, "GPS003", "运输中", "福银高速襄阳段", -18, 78),
    ("冀D22222", "刘师傅", "13800138004", 10, 40, "GPS004", "空闲", "杭州物流园", 4, 95),
    ("鲁E33333", "陈师傅", "13800138005", 5, 20, "GPS005", "空闲", "北京物流中心", -20, 100),
]

# (名称, 地址, 纬度, 经度, 容量m³, 已用, 面积, 温度, 湿度, 负责人, 电话)
_WAREHOUSES = [
    ("北京冷链中心", "北京市大兴区", 39.81, 116.42, 5000, 3200, 2500, -18, 45, "孙经理", "13700137001"),
    ("上海冷链中心", "上海市嘉定区", 31.23, 121.47, 4500, 2800, 2200, -20, 42, "钱经理", "13700137002"),
    ("广州冷链中心", "广州市白云区", 23.13, 113.26, 4000, 2100, 2000, -19, 48, "郑经理", "13700137003"),
    ("成都冷链中心", "成都市双流区", 30.57, 103.94, 3500, 1900, 1800, -18, 44, "冯经理", "13700137004"),
]

_TRANSPORTS = [
    dict(id="T0001", vehicle_no="京A12345", driver="张师傅", route="北京-上海", start_city="北京", end_city="上海",
         status="in_transit", temperature=-5.2, humidity=45.0, speed=85.0, fuel=72.0, cargo="新鲜蔬菜", weight=15.5,
         current_lat=35.04, current_lng=118.78, current_location="临沂服务区",
         departure_time=T("2026-09-29 06:00"), eta=T("2026-09-29 22:00"),
         waypoints=[{"lat": 39.90, "lng": 116.40, "name": "北京"}, {"lat": 36.65, "lng": 117.12, "name": "济南"},
                    {"lat": 35.04, "lng": 118.78, "name": "临沂"}, {"lat": 32.06, "lng": 118.78, "name": "南京"},
                    {"lat": 31.23, "lng": 121.47, "name": "上海"}],
         route_coords=[[116.40, 39.90], [117.12, 36.65], [118.78, 35.04], [118.78, 32.06], [121.47, 31.23]]),
    dict(id="T0002", vehicle_no="京B67890", driver="李师傅", route="广州-成都", start_city="广州", end_city="成都",
         status="in_transit", temperature=2.5, humidity=55.0, speed=78.0, fuel=65.0, cargo="新鲜水果", weight=18.0,
         current_lat=28.22, current_lng=112.98, current_location="长沙服务区",
         departure_time=T("2026-09-29 04:00"), eta=T("2026-09-30 12:00"),
         waypoints=[{"lat": 23.13, "lng": 113.26, "name": "广州"}, {"lat": 26.58, "lng": 111.32, "name": "桂林"},
                    {"lat": 28.22, "lng": 112.98, "name": "长沙"}, {"lat": 30.67, "lng": 104.06, "name": "成都"}],
         route_coords=[[113.26, 23.13], [111.32, 26.58], [112.98, 28.22], [104.06, 30.67]]),
    dict(id="T0003", vehicle_no="津C11111", driver="王师傅", route="武汉-西安", start_city="武汉", end_city="西安",
         status="in_transit", temperature=-17.5, humidity=50.0, speed=90.0, fuel=80.0, cargo="冷冻食品", weight=12.0,
         current_lat=32.63, current_lng=111.50, current_location="襄阳服务区",
         departure_time=T("2026-09-29 09:00"), eta=T("2026-09-29 20:00"),
         waypoints=[{"lat": 30.58, "lng": 114.30, "name": "武汉"}, {"lat": 32.63, "lng": 111.50, "name": "襄阳"},
                    {"lat": 34.27, "lng": 108.95, "name": "西安"}],
         route_coords=[[114.30, 30.58], [111.50, 32.63], [108.95, 34.27]]),
    dict(id="T0004", vehicle_no="冀D22222", driver="刘师傅", route="杭州-重庆", start_city="杭州", end_city="重庆",
         status="waiting", temperature=4.0, humidity=60.0, speed=0.0, fuel=95.0, cargo="乳制品", weight=8.0,
         current_lat=30.27, current_lng=120.15, current_location="杭州物流园",
         departure_time=T("2026-09-30 08:00"), eta=T("2026-10-01 18:00"),
         waypoints=[{"lat": 30.27, "lng": 120.15, "name": "杭州"}, {"lat": 29.56, "lng": 115.98, "name": "南昌"},
                    {"lat": 29.43, "lng": 106.55, "name": "重庆"}],
         route_coords=[[120.15, 30.27], [115.98, 29.56], [106.55, 29.43]]),
    dict(id="T0005", vehicle_no="鲁E33333", driver="陈师傅", route="深圳-北京", start_city="深圳", end_city="北京",
         status="arrived", temperature=-18.0, humidity=40.0, speed=0.0, fuel=30.0, cargo="冷冻肉类", weight=20.0,
         current_lat=39.90, current_lng=116.40, current_location="北京物流中心",
         departure_time=T("2026-09-27 20:00"), eta=T("2026-09-28 20:00"),
         waypoints=[{"lat": 22.54, "lng": 114.06, "name": "深圳"}, {"lat": 26.08, "lng": 119.30, "name": "福州"},
                    {"lat": 29.05, "lng": 120.15, "name": "杭州"}, {"lat": 31.85, "lng": 117.28, "name": "合肥"},
                    {"lat": 38.03, "lng": 114.48, "name": "石家庄"}, {"lat": 39.90, "lng": 116.40, "name": "北京"}],
         route_coords=[[114.06, 22.54], [119.30, 26.08], [120.15, 29.05], [117.28, 31.85], [114.48, 38.03],
                       [116.40, 39.90]]),
]

# ---------- WMS ----------

# (id, 字母, 名称, 类型, 仓库, 货主, 最低温, 最高温, 容量, 已用, 距出库口, 状态)
_ZONES = [
    ("Z0001", "A", "冷藏区A", "冷藏区", "北京冷链中心", "OW1001", 0, 5, 400, 280, 12, "正常"),
    ("Z0002", "B", "冷冻区A", "冷冻区", "北京冷链中心", "OW1001", -25, -18, 300, 250, 20, "正常"),
    ("Z0003", "C", "常温区A", "常温区", "北京冷链中心", None, 10, 25, 300, 120, 8, "正常"),
    ("Z0004", "D", "冷藏区B", "冷藏区", "上海冷链中心", "OW1002", 0, 5, 350, 150, 10, "正常"),
    ("Z0005", "E", "冷冻区B", "冷冻区", "上海冷链中心", "OW1002", -25, -18, 300, 210, 25, "正常"),
    ("Z0006", "F", "恒温区A", "恒温区", "上海冷链中心", "OW1004", 12, 16, 200, 60, 15, "正常"),
    ("Z0007", "G", "冷藏区C", "冷藏区", "广州冷链中心", "OW1003", 0, 5, 300, 290, 9, "正常"),
    ("Z0008", "H", "冷冻区C", "冷冻区", "广州冷链中心", "OW1005", -25, -18, 250, 90, 18, "正常"),
    ("Z0009", "J", "常温区B", "常温区", "广州冷链中心", "OW1005", 10, 25, 300, 100, 6, "正常"),
    ("Z0010", "K", "冷藏区D", "冷藏区", "成都冷链中心", "OW1003", 0, 5, 250, 60, 14, "维护中"),
    ("Z0011", "L", "冷冻区D", "冷冻区", "成都冷链中心", "OW1004", -25, -18, 200, 120, 22, "正常"),
    ("Z0012", "M", "常温区C", "常温区", "成都冷链中心", None, 10, 25, 200, 40, 7, "正常"),
]

_STD_ITEMS = ["外观检查", "色泽检查", "气味检查", "温度检测", "农残检测", "重金属检测"]

# (类型, 产品, 批次, 数量, 结果, 评分, 温度, 湿度, 农残, 重金属, 质检员, 地点, 备注, 时间)
_INSPECTIONS = [
    ("入库检查", "有机蔬菜", "BATCH2026090001", 150.5, "合格", 92.5, 3.2, 88.0, 0.12, 0.020, "质检员张伟", "北京冷链中心", "无异常", "2026-09-20 09:10"),
    ("入库检查", "新鲜水果", "BATCH2026090002", 220.0, "合格", 95.0, 4.1, 86.0, 0.08, 0.010, "质检员张伟", "北京冷链中心", "无异常", "2026-09-20 14:30"),
    ("在库检查", "冷冻肉类", "BATCH2026090003", 300.0, "合格", 90.0, -19.5, 78.0, 0.02, 0.015, "质检员刘芳", "上海冷链中心", "无异常", "2026-09-21 10:05"),
    ("出库检查", "乳制品", "BATCH2026090004", 80.0, "待复检", 68.0, 6.3, 82.0, 0.05, 0.010, "质检员刘芳", "上海冷链中心", "温度超标", "2026-09-21 16:40"),
    ("运输检查", "新鲜水果", "BATCH2026090005", 180.0, "合格", 88.5, 5.0, 85.0, 0.10, 0.020, "质检员陈刚", "广州冷链中心", "无异常", "2026-09-22 08:20"),
    ("入库检查", "土特产", "BATCH2026090006", 60.0, "合格", 94.0, 18.0, 55.0, 0.03, 0.010, "质检员陈刚", "广州冷链中心", "无异常", "2026-09-22 11:15"),
    ("终端检查", "有机蔬菜", "BATCH2026090007", 45.0, "不合格", 52.0, 9.8, 70.0, 0.62, 0.030, "质检员王敏", "成都冷链中心", "农药残留超标", "2026-09-23 09:00"),
    ("在库检查", "冷冻肉类", "BATCH2026090008", 260.0, "合格", 91.0, -20.1, 80.0, 0.01, 0.012, "质检员王敏", "成都冷链中心", "无异常", "2026-09-23 15:25"),
    ("入库检查", "乳制品", "BATCH2026090009", 120.0, "合格", 89.0, 3.8, 84.0, 0.04, 0.008, "质检员张伟", "北京冷链中心", "无异常", "2026-09-24 10:10"),
    ("出库检查", "新鲜水果", "BATCH2026090010", 95.0, "不合格", 48.5, 7.5, 88.0, 0.20, 0.020, "质检员刘芳", "上海冷链中心", "包装损坏", "2026-09-24 17:05"),
    ("运输检查", "冷冻肉类", "BATCH2026090011", 200.0, "合格", 93.0, -18.4, 76.0, 0.01, 0.010, "质检员陈刚", "广州冷链中心", "无异常", "2026-09-25 07:45"),
    ("在库检查", "有机蔬菜", "BATCH2026090012", 130.0, "待复检", 65.0, 5.9, 90.0, 0.35, 0.020, "质检员王敏", "成都冷链中心", "需要复检", "2026-09-25 13:30"),
    ("入库检查", "新鲜水果", "BATCH2026090013", 175.0, "合格", 96.5, 2.9, 87.0, 0.06, 0.010, "质检员张伟", "北京冷链中心", "无异常", "2026-09-26 09:40"),
    ("终端检查", "乳制品", "BATCH2026090014", 50.0, "合格", 87.0, 4.4, 83.0, 0.02, 0.005, "质检员刘芳", "上海冷链中心", "无异常", "2026-09-26 16:20"),
    ("入库检查", "冷冻肉类", "BATCH2026090015", 240.0, "不合格", 55.0, -12.0, 79.0, 0.02, 0.015, "质检员陈刚", "广州冷链中心", "温度超标", "2026-09-27 08:50"),
    ("在库检查", "土特产", "BATCH2026090016", 70.0, "合格", 90.5, 17.5, 52.0, 0.04, 0.010, "质检员王敏", "成都冷链中心", "无异常", "2026-09-27 14:15"),
    ("出库检查", "有机蔬菜", "BATCH2026090017", 110.0, "合格", 91.5, 3.5, 89.0, 0.09, 0.015, "质检员张伟", "北京冷链中心", "无异常", "2026-09-28 10:30"),
    ("运输检查", "乳制品", "BATCH2026090018", 65.0, "合格", 88.0, 4.8, 82.0, 0.03, 0.006, "质检员刘芳", "上海冷链中心", "无异常", "2026-09-28 15:55"),
    ("入库检查", "新鲜水果", "BATCH2026090019", 190.0, "合格", 94.5, 3.1, 86.0, 0.07, 0.010, "质检员陈刚", "广州冷链中心", "无异常", "2026-09-29 08:05"),
    ("在库检查", "冷冻肉类", "BATCH2026090020", 280.0, "合格", 92.0, -19.0, 77.0, 0.01, 0.010, "质检员王敏", "成都冷链中心", "无异常", "2026-09-29 11:20"),
]

# (id, 名称, 类型, 阈值, 单位, 品类, 通知渠道)
_RULES = [
    ("RULE001", "安全库存预警", "库存不足", 150, "件", ["蔬菜", "水果", "肉类"], ["短信", "邮件", "APP"]),
    ("RULE002", "临期预警", "临期预警", 7, "天", ["全部"], ["短信", "APP"]),
    ("RULE003", "库容预警", "库存过多", 90, "%", ["全部"], ["邮件"]),
    ("RULE004", "温度监控预警", "温度异常", 5, "°C", ["冷冻食品", "冷藏品"], ["短信", "邮件", "APP", "电话"]),
]

# (类型, 级别, 产品, SKU, 仓库, 温区, 当前值, 阈值, 单位, 状态, 创建时间, 处理时间)
_ALERTS = [
    ("库存不足", "critical", "有机蔬菜", "SKU001", "北京冷链中心", "冷藏区A", 12, 150, "件", "待处理", "2026-09-29 08:30", None),
    ("温度异常", "critical", "冷冻肉类", "SKU003", "广州冷链中心", "冷冻区C", -11.5, -18, "°C", "处理中", "2026-09-29 07:10", None),
    ("库存不足", "high", "新鲜水果", "SKU002", "上海冷链中心", "冷藏区B", 45, 150, "件", "待处理", "2026-09-28 16:20", None),
    ("临期预警", "high", "乳制品", "SKU005", "上海冷链中心", "冷藏区B", 3, 7, "天", "待处理", "2026-09-28 09:00", None),
    ("库存过多", "medium", "冷冻肉类", "SKU003", "北京冷链中心", "冷冻区A", 1180, 800, "件", "已确认", "2026-09-27 14:00", None),
    ("湿度异常", "medium", "土特产", "SKU004", "成都冷链中心", "常温区C", 82.5, 60, "%", "待处理", "2026-09-27 10:45", None),
    ("临期预警", "medium", "有机蔬菜", "SKU001", "广州冷链中心", "冷藏区C", 5, 7, "天", "处理中", "2026-09-26 18:30", None),
    ("库存不足", "medium", "乳制品", "SKU005", "成都冷链中心", "冷冻区D", 88, 150, "件", "待处理", "2026-09-26 11:00", None),
    ("温度异常", "high", "新鲜水果", "SKU002", "北京冷链中心", "冷藏区A", 7.8, 5, "°C", "已解决", "2026-09-25 22:15", "2026-09-26 01:30"),
    ("库存过多", "low", "土特产", "SKU004", "广州冷链中心", "常温区B", 920, 800, "件", "待处理", "2026-09-25 09:20", None),
    ("临期预警", "low", "新鲜水果", "SKU002", "成都冷链中心", "冷藏区D", 6, 7, "天", "已解决", "2026-09-24 15:00", "2026-09-25 10:00"),
    ("湿度异常", "low", "有机蔬菜", "SKU001", "上海冷链中心", "冷藏区B", 96.0, 95, "%", "已解决", "2026-09-23 08:40", "2026-09-23 12:10"),
    ("库存不足", "high", "冷冻肉类", "SKU003", "上海冷链中心", "冷冻区B", 30, 150, "件", "已解决", "2026-09-22 13:00", "2026-09-23 09:00"),
    ("温度异常", "medium", "乳制品", "SKU005", "成都冷链中心", "冷藏区D", 6.2, 5, "°C", "已解决", "2026-09-20 06:50", "2026-09-20 08:15"),
]

# 入库预约 (id, 货主编码, 车牌, 司机, 电话, 预计到达, 实际到达, 月台, 温区, 货物类型, 备注, 状态, 货物)
_APPOINTMENTS = [
    ("INB2026090001", "OW1001", "京A56789", "赵师傅", "13811110001", "2026-09-26 09:00", "2026-09-26 08:50", "D1", "冷藏区A", "生鲜果蔬", "", "已完成",
     [("SKU001", "有机蔬菜", 500, "6901234567890", "冷藏"), ("SKU002", "新鲜水果", 300, "6901234567891", "冷藏")]),
    ("INB2026090002", "OW1002", "沪B12345", "钱师傅", "13811110002", "2026-09-27 14:00", "2026-09-27 14:20", "D3", "冷冻区B", "冷冻肉类", "需要叉车", "已完成",
     [("SKU003", "冷冻肉类", 400, "6901234567892", "冷冻"), ("SKU006", "冷冻海鲜", 150, "6901234567895", "冷冻")]),
    ("INB2026090003", "OW1003", "粤A88888", "孙师傅", "13811110003", "2026-09-28 10:00", "2026-09-28 09:45", "D2", "冷藏区C", "乳制品", "加急", "收货中",
     [("SKU005", "纯牛奶", 600, "6901234567894", "冷藏"), ("SKU002", "新鲜水果", 200, "6901234567891", "冷藏"), ("SKU007", "矿泉水", 300, "6901234567896", "常温")]),
    ("INB2026090004", "OW1005", "粤B66666", "李师傅", "13811110004", "2026-09-29 08:00", "2026-09-29 08:10", "D5", "冷冻区C", "冷冻食品", "", "收货中",
     [("SKU003", "冷冻鸡胸肉", 250, "6901234567897", "冷冻"), ("SKU004", "土特产礼盒", 120, "6901234567893", "常温")]),
    ("INB2026090005", "OW1004", "苏A11111", "周师傅", "13811110005", "2026-09-29 15:00", "2026-09-29 14:40", "D4", "恒温区A", "进口水果", "", "已签到",
     [("SKU008", "进口车厘子", 180, "6901234567898", "冷藏")]),
    ("INB2026090006", "OW1001", "京C22222", "吴师傅", "13811110006", "2026-09-30 09:30", None, "D1", "冷藏区A", "生鲜果蔬", "散货", "待签到",
     [("SKU001", "有机蔬菜", 350, "6901234567890", "冷藏"), ("SKU009", "新鲜草莓", 120, "6901234567899", "冷藏")]),
    ("INB2026090007", "OW1002", "沪C33333", "郑师傅", "13811110007", "2026-09-30 13:00", None, "D2", "冷冻区B", "冷冻肉类", "", "待签到",
     [("SKU010", "冷冻猪肉", 280, "6901234567900", "冷冻")]),
    ("INB2026090008", "OW1003", "闽A44444", "冯师傅", "13811110008", "2026-10-01 10:00", None, "D3", "冷藏区C", "乳制品", "加急", "待签到",
     [("SKU005", "纯牛奶", 400, "6901234567894", "冷藏"), ("SKU011", "酸奶", 200, "6901234567901", "冷藏")]),
]

# 入库单 (id, 预约号, 货主, 仓库, 入库日期, 状态, 月台, 收货员, 创建时间,
#         明细[(sku, 名称, 条码, 存储, 预期, 已收, 合格, 温区, 货位)])
_ORDERS = [
    ("IOR2026090001", "INB2026090001", "本来生活网", "北京冷链中心", "2026-09-26", "已质检", "D1", "收货员甲", "2026-09-26 09:00",
     [("SKU001", "有机蔬菜", "6901234567890", "冷藏", 500, 500, 495, "Z0001", "A01-01-01"),
      ("SKU002", "新鲜水果", "6901234567891", "冷藏", 300, 300, 298, "Z0001", "A01-01-02")]),
    ("IOR2026090002", "INB2026090002", "盒马鲜生", "上海冷链中心", "2026-09-27", "已入库", "D3", "收货员乙", "2026-09-27 14:30",
     [("SKU003", "冷冻肉类", "6901234567892", "冷冻", 400, 400, 400, "Z0005", "E01-02-01"),
      ("SKU006", "冷冻海鲜", "6901234567895", "冷冻", 150, 150, 148, None, None)]),
    ("IOR2026090003", "INB2026090003", "永辉超市", "广州冷链中心", "2026-09-28", "收货中", "D2", "收货员丙", "2026-09-28 10:00",
     [("SKU005", "纯牛奶", "6901234567894", "冷藏", 600, 600, 596, None, None),
      ("SKU002", "新鲜水果", "6901234567891", "冷藏", 200, 120, 118, None, None),
      ("SKU007", "矿泉水", "6901234567896", "常温", 300, 0, 0, None, None)]),
    ("IOR2026090004", "INB2026090004", "沃尔玛中国", "广州冷链中心", "2026-09-29", "收货中", "D5", "收货员丙", "2026-09-29 08:20",
     [("SKU003", "冷冻鸡胸肉", "6901234567897", "冷冻", 250, 100, 100, None, None),
      ("SKU004", "土特产礼盒", "6901234567893", "常温", 120, 0, 0, None, None)]),
    ("IOR2026090005", None, "大润发", "成都冷链中心", "2026-09-29", "待收货", "D4", "收货员丁", "2026-09-29 09:30",
     [("SKU010", "冷冻猪肉", "6901234567900", "冷冻", 220, 0, 0, None, None),
      ("SKU009", "新鲜草莓", "6901234567899", "冷藏", 90, 0, 0, None, None)]),
]

# (工号, 姓名, 部门)
_OPERATORS = [
    ("EMP0001", "张磊", "收货组"), ("EMP0002", "李娜", "收货组"),
    ("EMP0003", "王强", "上架组"), ("EMP0004", "赵敏", "上架组"),
    ("EMP0005", "刘洋", "拣货组"), ("EMP0006", "陈静", "拣货组"),
    ("EMP0007", "杨帆", "复核组"), ("EMP0008", "黄勇", "发货组"),
]

# (类型, 优先级, 状态, 货主, 库位, 数量, 执行人, 分配时间, 开始, 完成, 错误数)
_TASKS = [
    ("收货", "高", "已完成", "本来生活网", "A01-01", 500, "张磊", "2026-09-26 09:00", "2026-09-26 09:05", "2026-09-26 09:50", 0),
    ("质检", "普通", "已完成", "本来生活网", "A01-01", 800, "李娜", "2026-09-26 10:00", "2026-09-26 10:05", "2026-09-26 10:40", 0),
    ("上架", "普通", "已完成", "本来生活网", "A01-02", 495, "王强", "2026-09-26 11:00", "2026-09-26 11:10", "2026-09-26 11:45", 1),
    ("收货", "紧急", "已完成", "盒马鲜生", "E01-02", 400, "李娜", "2026-09-27 14:30", "2026-09-27 14:35", "2026-09-27 15:20", 0),
    ("上架", "高", "已完成", "盒马鲜生", "E01-02", 400, "赵敏", "2026-09-27 15:30", "2026-09-27 15:40", "2026-09-27 16:10", 0),
    ("拣货", "高", "已完成", "盒马鲜生", "E02-05", 120, "刘洋", "2026-09-28 08:00", "2026-09-28 08:05", "2026-09-28 08:30", 1),
    ("复核", "高", "已完成", "盒马鲜生", "E02-05", 120, "杨帆", "2026-09-28 08:35", "2026-09-28 08:40", "2026-09-28 08:55", 0),
    ("发货", "高", "已完成", "盒马鲜生", "E02-05", 120, "黄勇", "2026-09-28 09:00", "2026-09-28 09:05", "2026-09-28 09:25", 0),
    ("收货", "紧急", "已完成", "永辉超市", "G01-01", 600, "张磊", "2026-09-28 10:00", "2026-09-28 10:05", "2026-09-28 11:00", 0),
    ("拣货", "普通", "已完成", "永辉超市", "G03-02", 80, "陈静", "2026-09-28 13:00", "2026-09-28 13:10", "2026-09-28 13:40", 2),
    ("补货", "低", "已完成", "永辉超市", "G03-02", 60, "王强", "2026-09-28 15:00", "2026-09-28 15:10", "2026-09-28 15:35", 0),
    ("盘点", "低", "已取消", "沃尔玛中国", "H01-01", 250, "赵敏", "2026-09-28 16:00", None, None, 0),
    ("收货", "紧急", "执行中", "沃尔玛中国", "H01-01", 250, "张磊", "2026-09-29 08:20", "2026-09-29 08:25", None, 0),
    ("收货", "高", "执行中", "永辉超市", "G01-02", 200, "李娜", "2026-09-29 09:00", "2026-09-29 09:05", None, 0),
    ("移库", "普通", "执行中", "大润发", "F01-03", 40, "王强", "2026-09-29 09:30", "2026-09-29 09:40", None, 0),
    ("拣货", "紧急", "待执行", "本来生活网", "A02-03", 60, "刘洋", "2026-09-29 10:00", None, None, 0),
    ("拣货", "高", "待执行", "本来生活网", "A02-05", 45, "刘洋", "2026-09-29 10:05", None, None, 0),
    ("拣货", "普通", "待执行", "本来生活网", "A03-01", 30, "陈静", "2026-09-29 10:10", None, None, 0),
    ("拣货", "高", "待执行", "盒马鲜生", "E02-01", 90, "陈静", "2026-09-29 13:00", None, None, 0),
    ("拣货", "普通", "待执行", "盒马鲜生", "E02-04", 70, "刘洋", "2026-09-29 13:10", None, None, 0),
    ("复核", "普通", "待执行", "永辉超市", "G03-02", 80, "杨帆", "2026-09-29 14:00", None, None, 0),
    ("打包", "普通", "待执行", "永辉超市", "G03-03", 80, "杨帆", "2026-09-29 14:20", None, None, 0),
    ("发货", "低", "待执行", "沃尔玛中国", "H02-01", 150, "黄勇", "2026-09-29 15:00", None, None, 0),
    ("盘点", "低", "待执行", "大润发", "L01-01", 120, "赵敏", "2026-09-29 16:00", None, None, 0),
]

# 各作业类型对应的货物（用于任务明细）
_SKU_BY_OWNER = {
    "本来生活网": ("SKU001", "有机蔬菜", "6901234567890"),
    "盒马鲜生": ("SKU003", "冷冻肉类", "6901234567892"),
    "永辉超市": ("SKU005", "纯牛奶", "6901234567894"),
    "沃尔玛中国": ("SKU003", "冷冻鸡胸肉", "6901234567897"),
    "大润发": ("SKU008", "进口车厘子", "6901234567898"),
}

# (id, 名称, 位置, 类型, 目标温度, 允许偏差, 基准温度偏移, 基准湿度)
_SENSORS = [
    ("SEN101", "北京冷链中心-冷冻库", "北京市大兴区", "冷库", -18, 2, 0.0, 45),
    ("SEN102", "上海冷链中心-冷冻库", "上海市嘉定区", "冷库", -20, 2, 0.3, 42),
    ("SEN103", "广州冷链中心-冷冻库", "广州市白云区", "冷库", -18, 2, 6.0, 48),  # 制冷故障，持续偏高
    ("SEN104", "成都冷链中心-冷藏库", "成都市双流区", "冷库", 3, 2, 0.2, 60),
    ("SEN201", "冷藏车 京A12345", "京沪高速临沂段", "冷藏车", -18, 3, 0.5, 45),
    ("SEN202", "冷藏车 京B67890", "京港澳高速长沙段", "冷藏车", 3, 2, 0.4, 55),
    ("SEN203", "冷藏车 津C11111", "福银高速襄阳段", "冷藏车", -18, 3, 0.4, 50),
]

# 温度告警 (传感器, 温度, 阈值, 级别, 状态, 时间)
_TEMP_ALERTS = [
    ("SEN103", -12.0, -16, "critical", "未处理", "2026-09-29 14:00"),
    ("SEN103", -13.5, -16, "warning", "处理中", "2026-09-29 10:00"),
    ("SEN202", 5.8, 5, "warning", "已解决", "2026-09-28 22:00"),
    ("SEN201", -14.2, -15, "warning", "已解决", "2026-09-28 18:00"),
    ("SEN104", 5.6, 5, "warning", "已解决", "2026-09-27 06:00"),
    ("SEN102", -17.2, -18, "warning", "已解决", "2026-09-26 12:00"),
]

# (月份, 电费, 燃油, 维护)
_COSTS = [
    ("2026-07", 118500.0, 62300.0, 18400.0),
    ("2026-08", 126800.0, 65900.0, 15200.0),
    ("2026-09", 121300.0, 60800.0, 21600.0),
]


def _readings_for(sensor) -> list:
    """生成固定的 24 小时读数（每 2 小时一条，数学公式推导，非随机）"""
    sid, _, _, _, target, _, offset, humidity = sensor
    seed = int(sid[3:])
    rows = []
    start = T("2026-09-29 00:00")
    for i in range(12):
        # 以正弦波模拟压缩机启停造成的温度周期波动，幅度 0.8°C
        wave = 0.8 * math.sin((i + seed) * math.pi / 6)
        rows.append(TemperatureReading(
            sensor_id=sid,
            temperature=round(target + offset + wave, 1),
            humidity=round(humidity + 3 * math.cos((i + seed) * math.pi / 6), 1),
            recorded_at=start + timedelta(hours=2 * i),
        ))
    return rows


def _empty(db: Session, model) -> bool:
    return db.query(model).first() is None


def seed_cold_chain(db: Session) -> bool:
    """写入默认数据；有新数据写入时返回 True"""
    created = False

    if _empty(db, CargoOwner):
        for code, name, contact, phone, email, address in _OWNERS:
            db.add(CargoOwner(code=code, name=name, contact=contact, phone=phone, email=email,
                              address=address, status="正常"))
        created = True

    if _empty(db, Vehicle):
        for plate, driver, phone, load, volume, gps, status, loc, temp, battery in _VEHICLES:
            db.add(Vehicle(plate=plate, vehicle_type="冷藏车", driver=driver, phone=phone, load_capacity=load,
                           volume=volume, gps_device=gps, temp_range="-25°C~5°C", status=status,
                           location=loc, temperature=temp, battery=battery))
        created = True

    if _empty(db, Warehouse):
        for i, (name, address, lat, lng, cap, used, area, temp, hum, manager, phone) in enumerate(_WAREHOUSES, 1):
            db.add(Warehouse(id=f"W{i:04d}", name=name, address=address, lat=lat, lng=lng, capacity=cap, used=used, area=area,
                             temperature=temp, humidity=hum, inventory=0, manager=manager, phone=phone,
                             status="正常"))
        created = True

    if _empty(db, Transport):
        for t in _TRANSPORTS:
            db.add(Transport(**t))
        created = True

    if _empty(db, StorageZone):
        for zid, code, name, ztype, wh, owner, tmin, tmax, cap, used, dist, status in _ZONES:
            db.add(StorageZone(id=zid, code=code, name=name, type=ztype, warehouse=wh, owner_code=owner,
                               temperature_min=tmin, temperature_max=tmax, capacity=cap, used=used,
                               distance_to_pick=dist, status=status))
        created = True

    if _empty(db, QualityInspection):
        for i, (itype, product, batch, qty, result, score, temp, hum, pest, metal, inspector, loc, remark,
                ts) in enumerate(_INSPECTIONS, start=1):
            items = [{"name": n, "result": result if n == "温度检测" and remark == "温度超标" else "合格",
                      "score": score} for n in _STD_ITEMS]
            db.add(QualityInspection(id=f"QC{i:05d}", type=itype, product=product, batch_no=batch, quantity=qty,
                                     result=result, score=score, temperature=temp, humidity=hum,
                                     pesticide_residue=pest, heavy_metal=metal, inspector=inspector, location=loc,
                                     remark=remark, items=items, created_at=T(ts)))
        created = True

    if _empty(db, InventoryRule):
        for rid, name, rtype, threshold, unit, cats, channels in _RULES:
            db.add(InventoryRule(id=rid, name=name, type=rtype, enabled=True, threshold=threshold, unit=unit,
                                 product_categories=cats, notify_channels=channels))
        created = True

    if _empty(db, InventoryAlert):
        for i, (atype, level, product, sku, wh, zone, cur, thr, unit, status, ts, resolved) in enumerate(
                _ALERTS, start=1):
            db.add(InventoryAlert(id=f"IA{i:04d}", type=atype, level=level, product=product, product_code=sku,
                                  warehouse=wh, zone=zone, current_value=cur, threshold=thr, unit=unit,
                                  status=status, created_at=T(ts), resolved_at=T(resolved) if resolved else None))
        created = True

    owners = {code: name for code, name, *_ in _OWNERS}
    if _empty(db, InboundAppointment):
        for aid, ocode, vno, driver, phone, eta, actual, dock, zone, cargo, remark, status, goods in _APPOINTMENTS:
            items = [{"sku": s, "name": n, "quantity": q, "unit": "件", "barcode": b, "storage_type": st}
                     for s, n, q, b, st in goods]
            db.add(InboundAppointment(id=aid, owner=owners[ocode], owner_code=ocode, vehicle_no=vno, driver=driver,
                                      driver_phone=phone, estimated_arrival=T(eta),
                                      actual_arrival=T(actual) if actual else None, dock=dock, zone=zone,
                                      cargo_type=cargo, remark=remark, items=items, status=status,
                                      created_at=T(eta) - timedelta(days=2)))
        created = True

    if _empty(db, InboundOrder):
        for oid, aid, owner, wh, day, status, dock, receiver, ts, lines in _ORDERS:
            order = InboundOrder(id=oid, appointment_id=aid, owner=owner, warehouse=wh, inbound_date=day,
                                 status=status, dock=dock, receiver=receiver, created_at=T(ts))
            for sku, name, barcode, st, exp, rec, qual, zone_id, loc in lines:
                order.items.append(InboundOrderItem(sku=sku, name=name, barcode=barcode, storage_type=st,
                                                    expected_qty=exp, received_qty=rec, qualified_qty=qual,
                                                    zone_id=zone_id, location=loc))
            db.add(order)
        created = True

    if _empty(db, Operator):
        for emp_id, name, dept in _OPERATORS:
            db.add(Operator(employee_id=emp_id, name=name, department=dept))
        created = True

    if _empty(db, OperationTask):
        for i, (ttype, prio, status, owner, loc, qty, who, assigned, started, done, errors) in enumerate(
                _TASKS, start=1):
            sku, pname, barcode = _SKU_BY_OWNER[owner]
            history = [{"action": "任务分配", "operator": "系统", "time": assigned}]
            if started:
                history.append({"action": "开始执行", "operator": who, "time": started})
            if done:
                history.append({"action": "完成任务", "operator": who, "time": done})
            if status == "已取消":
                history.append({"action": "取消任务", "operator": "系统", "time": assigned})
            db.add(OperationTask(
                id=f"TSK{i:05d}", type=ttype, priority=prio, status=status, owner=owner, location=loc,
                target_location=f"{loc}-{i % 30 + 1:02d}", quantity=qty, assigned_to=who, assigned_at=T(assigned),
                started_at=T(started) if started else None, completed_at=T(done) if done else None,
                barcode=f"BC{260900 + i}", error_count=errors,
                items=[{"sku": sku, "name": pname, "barcode": barcode, "quantity": qty, "location": loc}],
                history=history))
        created = True

    if _empty(db, TemperatureSensor):
        for s in _SENSORS:
            sid, name, loc, kind, target, tol, _, _ = s
            db.add(TemperatureSensor(id=sid, name=name, location=loc, kind=kind, target_temp=target, tolerance=tol))
            db.add_all(_readings_for(s))
        created = True

    if _empty(db, TemperatureAlert):
        names = {s[0]: s[1] for s in _SENSORS}
        for i, (sid, temp, thr, severity, status, ts) in enumerate(_TEMP_ALERTS, start=1):
            db.add(TemperatureAlert(id=f"A{i:04d}", sensor_id=sid, location=names[sid], type="温度异常",
                                    temperature=temp, threshold=thr, severity=severity, status=status,
                                    message="温度超过阈值" if severity == "warning" else "温度严重超标",
                                    timestamp=T(ts)))
        created = True

    if _empty(db, OperatingCost):
        for month, elec, fuel, maint in _COSTS:
            db.add_all([OperatingCost(month=month, category="electricity", amount=elec),
                        OperatingCost(month=month, category="fuel", amount=fuel),
                        OperatingCost(month=month, category="maintenance", amount=maint)])
        created = True

    if created:
        db.commit()
    return created
