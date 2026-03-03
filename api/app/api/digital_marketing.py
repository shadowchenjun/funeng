"""
数字营销API
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random

router = APIRouter()

# 电商订单模型
class Order(BaseModel):
    id: str
    customer_name: str
    product: str
    quantity: int
    price: float
    status: str
    channel: str  # 渠道: app/web/小程序/直播
    created_at: str

# 会员数据模型
class Member(BaseModel):
    id: str
    name: str
    level: str  # 普通/银卡/金卡/钻石
    points: int
    total_spent: float
    join_date: str

# 直播数据模型
class LiveStream(BaseModel):
    id: str
    title: str
    host: str
    status: str  # planning/live/ended
    viewers: int
    likes: int
    orders: int
    revenue: float

@router.get("/orders")
def get_orders():
    """获取电商订单列表"""
    statuses = ["待付款", "待发货", "配送中", "已完成", "已取消"]
    channels = ["APP", "小程序", "网页", "直播间"]
    products = ["有机大米", "新鲜蔬菜", "水果礼盒", "土特产", "有机水果"]
    
    orders = []
    for i in range(20):
        date = datetime.now() - timedelta(hours=random.randint(0, 72))
        orders.append({
            "id": f"ORD{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
            "customer_name": f"客户{i+1}",
            "product": random.choice(products),
            "quantity": random.randint(1, 10),
            "price": round(random.uniform(50, 500), 2),
            "status": random.choice(statuses),
            "channel": random.choice(channels),
            "created_at": date.isoformat()
        })
    return orders

@router.get("/orders/stats")
def get_order_stats():
    """获取订单统计数据"""
    return {
        "today": {
            "orders": random.randint(50, 200),
            "revenue": round(random.uniform(5000, 20000), 2),
            "avg_price": round(random.uniform(80, 200), 2)
        },
        "yesterday": {
            "orders": random.randint(50, 200),
            "revenue": round(random.uniform(5000, 20000), 2),
            "avg_price": round(random.uniform(80, 200), 2)
        },
        "week": {
            "orders": random.randint(500, 1500),
            "revenue": round(random.uniform(50000, 150000), 2),
            "growth": round(random.uniform(-10, 30), 1)
        },
        "month": {
            "orders": random.randint(2000, 6000),
            "revenue": round(random.uniform(200000, 600000), 2),
            "growth": round(random.uniform(-5, 25), 1)
        }
    }

@router.get("/channel-stats")
def get_channel_stats():
    """获取销售渠道统计"""
    channels = [
        {"name": "APP", "orders": random.randint(100, 500), "revenue": random.randint(10000, 50000)},
        {"name": "小程序", "orders": random.randint(100, 500), "revenue": random.randint(10000, 50000)},
        {"name": "网页", "orders": random.randint(50, 300), "revenue": random.randint(5000, 30000)},
        {"name": "直播间", "orders": random.randint(200, 800), "revenue": random.randint(20000, 100000)}
    ]
    return channels

@router.get("/members")
def get_members():
    """获取会员列表"""
    levels = ["普通会员", "银卡会员", "金卡会员", "钻石会员"]
    members = []
    
    for i in range(30):
        join_date = datetime.now() - timedelta(days=random.randint(30, 730))
        level = random.choice(levels)
        base_points = {"普通会员": 100, "银卡会员": 2000, "金卡会员": 10000, "钻石会员": 50000}
        
        members.append({
            "id": f"M{i+1:05d}",
            "name": f"会员{i+1}",
            "level": level,
            "points": random.randint(base_points[level], base_points[level] * 5),
            "total_spent": round(random.uniform(100, 50000), 2),
            "orders": random.randint(1, 200),
            "join_date": join_date.strftime("%Y-%m-%d"),
            "last_active": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
        })
    return members

@router.get("/members/stats")
def get_member_stats():
    """获取会员统计数据"""
    return {
        "total": random.randint(5000, 20000),
        "new_today": random.randint(10, 100),
        "active": random.randint(1000, 5000),
        "by_level": {
            "普通会员": random.randint(3000, 10000),
            "银卡会员": random.randint(1000, 3000),
            "金卡会员": random.randint(300, 1000),
            "钻石会员": random.randint(50, 300)
        },
        "points_total": random.randint(1000000, 5000000),
        "conversion_rate": round(random.uniform(2, 8), 1)
    }

@router.get("/members/levels")
def get_member_levels():
    """获取会员等级配置"""
    return [
        {"level": "普通会员", "threshold": 0, "discount": 1.0, "points_rate": 1.0, "color": "#909399"},
        {"level": "银卡会员", "threshold": 2000, "discount": 0.95, "points_rate": 1.5, "color": "#C0C4CC"},
        {"level": "金卡会员", "threshold": 10000, "discount": 0.9, "points_rate": 2.0, "color": "#E6A23C"},
        {"level": "钻石会员", "threshold": 50000, "discount": 0.85, "points_rate": 3.0, "color": "#F56C6C"}
    ]

@router.get("/live")
def get_live_streams():
    """获取直播列表"""
    hosts = ["李老师", "王主播", "小美", "农博士", "田野哥"]
    titles = ["新鲜蔬果专场", "有机大米特惠", "家乡味道", "产地直供", "限时秒杀"]
    statuses = ["planning", "live", "ended"]
    
    streams = []
    for i in range(10):
        status = random.choice(statuses)
        streams.append({
            "id": f"L{i+1:03d}",
            "title": random.choice(titles),
            "host": random.choice(hosts),
            "status": status,
            "viewers": random.randint(100, 10000) if status == "live" else random.randint(1000, 50000),
            "likes": random.randint(500, 100000),
            "orders": random.randint(10, 500),
            "revenue": round(random.uniform(1000, 50000), 2),
            "duration": random.randint(30, 180) if status == "ended" else random.randint(0, 120),
            "scheduled_time": (datetime.now() + timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M"),
            "cover_image": f"https://picsum.photos/seed/live{i}/400/225"
        })
    return streams

@router.get("/live/{stream_id}")
def get_live_stream(stream_id: str):
    """获取直播详情"""
    return {
        "id": stream_id,
        "title": "新鲜蔬果专场",
        "host": "李老师",
        "status": "live",
        "viewers": random.randint(1000, 10000),
        "likes": random.randint(5000, 50000),
        "orders": random.randint(50, 500),
        "revenue": round(random.uniform(5000, 50000), 2),
        "comments": random.randint(100, 1000),
        "products": [
            {"name": "有机大米5kg", "price": 68, "sold": random.randint(50, 500), "stock": 1000},
            {"name": "新鲜蔬菜礼盒", "price": 128, "sold": random.randint(20, 200), "stock": 500},
            {"name": "土特产套装", "price": 258, "sold": random.randint(10, 100), "stock": 200}
        ]
    }

@router.get("/marketing/campaigns")
def get_marketing_campaigns():
    """获取营销活动列表"""
    campaigns = []
    statuses = ["进行中", "待开始", "已结束"]
    types = ["满减", "折扣", "秒杀", "拼团", "会员日"]
    
    for i in range(10):
        start_date = datetime.now() - timedelta(days=random.randint(0, 30))
        end_date = start_date + timedelta(days=random.randint(7, 30))
        status = "进行中" if start_date <= datetime.now() <= end_date else ("待开始" if start_date > datetime.now() else "已结束")
        
        campaigns.append({
            "id": f"C{i+1:03d}",
            "name": f"{random.choice(types)}活动{i+1}",
            "type": random.choice(types),
            "status": status,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "participants": random.randint(100, 10000),
            "orders": random.randint(50, 1000),
            "revenue": round(random.uniform(5000, 100000), 2)
        })
    return campaigns

@router.get("/analytics")
def get_marketing_analytics():
    """获取营销分析数据"""
    return {
        "overview": {
            "total_orders": random.randint(10000, 50000),
            "total_revenue": round(random.uniform(1000000, 5000000), 2),
            "avg_order_value": round(random.uniform(100, 300), 2),
            "conversion_rate": round(random.uniform(2, 8), 1)
        },
        "growth": {
            "orders_growth": round(random.uniform(-5, 30), 1),
            "revenue_growth": round(random.uniform(-3, 35), 1),
            "member_growth": round(random.uniform(5, 25), 1)
        },
        "top_products": [
            {"name": "有机大米", "sales": random.randint(1000, 5000), "revenue": random.randint(50000, 300000)},
            {"name": "新鲜蔬菜", "sales": random.randint(800, 4000), "revenue": random.randint(40000, 200000)},
            {"name": "水果礼盒", "sales": random.randint(500, 3000), "revenue": random.randint(30000, 200000)}
        ]
    }
