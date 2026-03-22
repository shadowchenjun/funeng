"""
数据看板API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models.admin import (
    AdminUser, AdoptionOrder, RentalOrder, LandParcel,
    Device, DeviceLog
)
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.api.admin.auth import get_current_admin

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取看板统计数据"""
    today = datetime.now().date()
    month_start = today.replace(day=1)

    # 用户统计
    total_users = db.query(User).count()
    new_users_today = db.query(User).filter(func.date(User.created_at) == today).count()
    new_users_month = db.query(User).filter(func.date(User.created_at) >= month_start).count()

    # 土地统计
    total_land = db.query(LandParcel).count()
    available_land = db.query(LandParcel).filter(LandParcel.status == "available").count()
    rented_land = db.query(LandParcel).filter(LandParcel.status == "rented").count()

    # 认养订单统计
    total_adoption_orders = db.query(AdoptionOrder).count()
    adoption_orders_today = db.query(AdoptionOrder).filter(func.date(AdoptionOrder.created_at) == today).count()
    pending_adoption = db.query(AdoptionOrder).filter(AdoptionOrder.status == "pending").count()
    active_adoption = db.query(AdoptionOrder).filter(AdoptionOrder.status == "active").count()

    # 认养收入
    adoption_revenue = db.query(func.sum(AdoptionOrder.total_amount)).filter(
        AdoptionOrder.status.in_(["paid", "active", "completed"])
    ).scalar() or 0

    # 租地订单统计
    total_rental_orders = db.query(RentalOrder).count()
    rental_orders_today = db.query(RentalOrder).filter(func.date(RentalOrder.created_at) == today).count()
    pending_rental = db.query(RentalOrder).filter(RentalOrder.status == "pending").count()

    # 租地收入
    rental_revenue = db.query(func.sum(RentalOrder.total_amount)).filter(
        RentalOrder.status.in_(["paid", "active", "completed"])
    ).scalar() or 0

    # 设备统计
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    offline_devices = db.query(Device).filter(Device.status == "offline").count()

    # 产品统计
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()

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
            "revenue": adoption_revenue
        },
        "rental_orders": {
            "total": total_rental_orders,
            "today": rental_orders_today,
            "pending": pending_rental,
            "revenue": rental_revenue
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


@router.get("/charts")
def get_dashboard_charts(
    days: int = 7,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取看板图表数据"""
    today = datetime.now().date()
    start_date = today - timedelta(days=days-1)

    # 每日订单数据
    daily_orders = []
    daily_revenue = []

    for i in range(days):
        date = start_date + timedelta(days=i)
        adoption_count = db.query(AdoptionOrder).filter(func.date(AdoptionOrder.created_at) == date).count()
        rental_count = db.query(RentalOrder).filter(func.date(RentalOrder.created_at) == date).count()
        adoption_rev = db.query(func.sum(AdoptionOrder.total_amount)).filter(
            func.date(AdoptionOrder.created_at) == date,
            AdoptionOrder.status.in_(["paid", "active", "completed"])
        ).scalar() or 0
        rental_rev = db.query(func.sum(RentalOrder.total_amount)).filter(
            func.date(RentalOrder.created_at) == date,
            RentalOrder.status.in_(["paid", "active", "completed"])
        ).scalar() or 0

        daily_orders.append({
            "date": date.isoformat(),
            "adoption": adoption_count,
            "rental": rental_count,
            "total": adoption_count + rental_count
        })
        daily_revenue.append({
            "date": date.isoformat(),
            "adoption": float(adoption_rev),
            "rental": float(rental_rev),
            "total": float(adoption_rev + rental_rev)
        })

    # 土地使用情况
    land_status = db.query(
        LandParcel.status, func.count(LandParcel.id)
    ).group_by(LandParcel.status).all()

    land_usage = [
        {"status": status, "count": count}
        for status, count in land_status
    ]

    # 设备状态
    device_status = db.query(
        Device.status, func.count(Device.id)
    ).group_by(Device.status).all()

    device_status_list = [
        {"status": status, "count": count}
        for status, count in device_status
    ]

    # 认养分类统计
    from app.models.admin import AdoptionConfig
    category_stats = db.query(
        AdoptionConfig.name, func.count(AdoptionOrder.id)
    ).join(AdoptionOrder, AdoptionOrder.config_id == AdoptionConfig.id)\
     .group_by(AdoptionConfig.name).limit(5).all()

    category_data = [
        {"name": name, "count": count}
        for name, count in category_stats
    ]

    return {
        "daily_orders": daily_orders,
        "daily_revenue": daily_revenue,
        "land_usage": land_usage,
        "device_status": device_status_list,
        "category_data": category_data
    }


@router.get("/recent-orders")
def get_recent_orders(
    limit: int = 10,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取最近订单"""
    # 认养订单
    adoption_orders = db.query(AdoptionOrder).order_by(
        AdoptionOrder.created_at.desc()
    ).limit(limit).all()

    # 租地订单
    rental_orders = db.query(RentalOrder).order_by(
        RentalOrder.created_at.desc()
    ).limit(limit).all()

    return {
        "adoption_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user": o.user.username if o.user else "未知",
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
                "user": o.user.username if o.user else "未知",
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at
            }
            for o in rental_orders
        ]
    }
