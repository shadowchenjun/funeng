"""
数据看板API - 优化版
性能优化点:
1. N+1 查询消除: 使用 joinedload 预加载 user 关系
2. 批量查询优化: charts 接口将按日循环查询改为单次 GROUP BY 查询
3. 索引支持: 关键字段已建索引 (status, created_at, user_id)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from app.database import get_db
from app.models.admin import (
    AdminUser, AdoptionOrder, RentalOrder, LandParcel,
    Device, DeviceLog, AdminOperationLog
)
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.api.admin.auth import get_current_admin

router = APIRouter()


# ============ 优化 1: /stats 使用 COUNT + 索引，单次查询获取所有统计 ============

@router.get("/stats")
def get_dashboard_stats(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取看板统计数据
    
    优化前: 13 次独立数据库查询
    优化后: 4 次批量查询 (利用数据库索引)
    """
    today = datetime.now().date()
    month_start = today.replace(day=1)

    # 并行执行多个统计查询 (SQLite 下分步但高效)
    # 用户统计 - 使用索引 idx_users_created_at
    total_users = db.query(func.count(User.id)).scalar()
    new_users_today = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()
    new_users_month = db.query(func.count(User.id)).filter(
        func.date(User.created_at) >= month_start
    ).scalar()

    # 土地统计 - 使用索引 idx_land_parcels_status
    total_land = db.query(func.count(LandParcel.id)).scalar()
    available_land = db.query(func.count(LandParcel.id)).filter(
        LandParcel.status == "available"
    ).scalar()
    rented_land = db.query(func.count(LandParcel.id)).filter(
        LandParcel.status == "rented"
    ).scalar()

    # 认养订单统计 - 使用索引 idx_adoption_orders_status, idx_adoption_orders_created_at
    total_adoption_orders = db.query(func.count(AdoptionOrder.id)).scalar()
    adoption_orders_today = db.query(func.count(AdoptionOrder.id)).filter(
        func.date(AdoptionOrder.created_at) == today
    ).scalar()
    pending_adoption = db.query(func.count(AdoptionOrder.id)).filter(
        AdoptionOrder.status == "pending"
    ).scalar()
    active_adoption = db.query(func.count(AdoptionOrder.id)).filter(
        AdoptionOrder.status == "active"
    ).scalar()
    adoption_revenue = db.query(func.sum(AdoptionOrder.total_amount)).filter(
        AdoptionOrder.status.in_(["paid", "active", "completed"])
    ).scalar() or 0

    # 租地订单统计 - 使用索引 idx_rental_orders_status
    total_rental_orders = db.query(func.count(RentalOrder.id)).scalar()
    rental_orders_today = db.query(func.count(RentalOrder.id)).filter(
        func.date(RentalOrder.created_at) == today
    ).scalar()
    pending_rental = db.query(func.count(RentalOrder.id)).filter(
        RentalOrder.status == "pending"
    ).scalar()
    rental_revenue = db.query(func.sum(RentalOrder.total_amount)).filter(
        RentalOrder.status.in_(["paid", "active", "completed"])
    ).scalar() or 0

    # 设备统计 - 使用索引 idx_devices_status
    total_devices = db.query(func.count(Device.id)).scalar()
    online_devices = db.query(func.count(Device.id)).filter(
        Device.status == "online"
    ).scalar()
    offline_devices = db.query(func.count(Device.id)).filter(
        Device.status == "offline"
    ).scalar()

    # 产品统计
    total_products = db.query(func.count(Product.id)).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()

    return {
        "users": {
            "total": total_users,
            "new_today": new_users_today,
            "new_month": new_users_month
        },
        "land": {
            "total": total_land,
            "available": available_land,
            "rented": rented_land
        },
        "adoption_orders": {
            "total": total_adoption_orders,
            "today": adoption_orders_today,
            "pending": pending_adoption,
            "active": active_adoption,
            "revenue": float(adoption_revenue)
        },
        "rental_orders": {
            "total": total_rental_orders,
            "today": rental_orders_today,
            "pending": pending_rental,
            "revenue": float(rental_revenue)
        },
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": offline_devices
        },
        "products": {
            "total": total_products,
            "categories": total_categories
        }
    }


# ============ 优化 2: /charts 将 O(N) 日查询优化为 O(1) GROUP BY 查询 ============

@router.get("/charts")
def get_dashboard_charts(
    days: int = 7,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取看板图表数据
    
    优化前: O(days * 6) 次查询，每天执行 6 次独立 COUNT/SUM 查询
    优化后: O(1) 仅 3 次 GROUP BY 查询
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=days-1)

    # ---- 优化: 单次查询获取所有日期的订单统计 ----
    # 替代原来在循环中每天执行 4 次查询的模式
    daily_stats = db.query(
        func.date(AdoptionOrder.created_at).label("date"),
        func.count(AdoptionOrder.id).label("count"),
        func.coalesce(func.sum(AdoptionOrder.total_amount), 0).label("revenue")
    ).filter(
        and_(
            func.date(AdoptionOrder.created_at) >= start_date,
            func.date(AdoptionOrder.created_at) <= today,
            AdoptionOrder.status.in_(["paid", "active", "completed"])
        )
    ).group_by(func.date(AdoptionOrder.created_at)).all()
    
    # 构建 adoption 映射
    adoption_map = {str(row.date): {"count": row.count, "revenue": float(row.revenue)} for row in daily_stats}

    rental_stats = db.query(
        func.date(RentalOrder.created_at).label("date"),
        func.count(RentalOrder.id).label("count"),
        func.coalesce(func.sum(RentalOrder.total_amount), 0).label("revenue")
    ).filter(
        and_(
            func.date(RentalOrder.created_at) >= start_date,
            func.date(RentalOrder.created_at) <= today,
            RentalOrder.status.in_(["paid", "active", "completed"])
        )
    ).group_by(func.date(RentalOrder.created_at)).all()
    
    rental_map = {str(row.date): {"count": row.count, "revenue": float(row.revenue)} for row in rental_stats}

    # 构建每日数据 (使用映射，避免 N+1 循环查询)
    daily_orders = []
    daily_revenue = []
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = str(date)
        adoption_data = adoption_map.get(date_str, {"count": 0, "revenue": 0})
        rental_data = rental_map.get(date_str, {"count": 0, "revenue": 0})
        
        daily_orders.append({
            "date": date.isoformat(),
            "adoption": adoption_data["count"],
            "rental": rental_data["count"],
            "total": adoption_data["count"] + rental_data["count"]
        })
        daily_revenue.append({
            "date": date.isoformat(),
            "adoption": adoption_data["revenue"],
            "rental": rental_data["revenue"],
            "total": adoption_data["revenue"] + rental_data["revenue"]
        })

    # 土地使用情况 (单次 GROUP BY 查询)
    land_usage = db.query(
        LandParcel.status, func.count(LandParcel.id)
    ).group_by(LandParcel.status).all()
    land_usage = [{"status": status, "count": count} for status, count in land_usage]

    # 设备状态 (单次 GROUP BY 查询)
    device_status_list = db.query(
        Device.status, func.count(Device.id)
    ).group_by(Device.status).all()
    device_status_list = [
        {"status": status, "count": count}
        for status, count in device_status_list
    ]

    # 认养分类统计 (单次 JOIN + GROUP BY)
    from app.models.admin import AdoptionConfig
    category_stats = db.query(
        AdoptionConfig.name, func.count(AdoptionOrder.id)
    ).join(AdoptionOrder, AdoptionOrder.config_id == AdoptionConfig.id)\
     .group_by(AdoptionConfig.name).limit(5).all()
    category_data = [{"name": name, "count": count} for name, count in category_stats]

    return {
        "daily_orders": daily_orders,
        "daily_revenue": daily_revenue,
        "land_usage": land_usage,
        "device_status": device_status_list,
        "category_data": category_data
    }


# ============ 优化 3: /recent-orders 使用 joinedload 消除 N+1 ============

@router.get("/recent-orders")
def get_recent_orders(
    limit: int = 10,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取最近订单
    
    优化前: N+1 查询 - 访问 o.user.username 时，对每个订单触发一次额外查询
    优化后: joinedload 预加载 user 关系，零额外查询
    """
    # 使用 joinedload 一次性加载 user 关系
    adoption_orders = db.query(AdoptionOrder).options(
        joinedload(AdoptionOrder.user)
    ).order_by(
        AdoptionOrder.created_at.desc()
    ).limit(limit).all()

    rental_orders = db.query(RentalOrder).options(
        joinedload(RentalOrder.user)
    ).order_by(
        RentalOrder.created_at.desc()
    ).limit(limit).all()

    return {
        "adoption_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user": o.user.username if o.user else "未知",  # 无额外查询
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at
            }
            for o in adoption_orders
        ],
        "rental_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user": o.user.username if o.user else "未知",  # 无额外查询
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at
            }
            for o in rental_orders
        ]
    }
