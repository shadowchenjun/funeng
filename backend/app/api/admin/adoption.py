"""
认养管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional, List
import json

from app.database import get_db
from app.models.admin import (
    AdminUser, AdoptionCategory, AdoptionConfig, AdoptionOrder, LandParcel
)
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


# ============ 认养分类 ============

@router.get("/categories")
def list_categories(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取认养分类列表"""
    categories = db.query(AdoptionCategory).order_by(AdoptionCategory.sort_order).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "icon": c.icon,
            "description": c.description,
            "sort_order": c.sort_order,
            "is_active": c.is_active,
            "created_at": c.created_at
        }
        for c in categories
    ]


@router.post("/categories")
def create_category(
    name: str,
    code: str,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: int = 0,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建认养分类"""
    existing = db.query(AdoptionCategory).filter(AdoptionCategory.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类代码已存在")

    category = AdoptionCategory(
        name=name,
        code=code,
        icon=icon,
        description=description,
        sort_order=sort_order
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    log_operation(db, current_admin.id, "create", "adoption_category", category.id, f"创建认养分类: {name}")

    return {"id": category.id, "message": "创建成功"}


@router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新认养分类"""
    category = db.query(AdoptionCategory).filter(AdoptionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    if name:
        category.name = name
    if icon:
        category.icon = icon
    if description:
        category.description = description
    if sort_order is not None:
        category.sort_order = sort_order
    if is_active is not None:
        category.is_active = is_active

    category.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "adoption_category", category_id, f"更新认养分类: {name}")

    return {"message": "更新成功"}


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除认养分类"""
    category = db.query(AdoptionCategory).filter(AdoptionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 检查是否有配置关联
    configs = db.query(AdoptionConfig).filter(AdoptionConfig.category_id == category_id).count()
    if configs > 0:
        raise HTTPException(status_code=400, detail="该分类下有认养配置，无法删除")

    db.delete(category)
    db.commit()

    log_operation(db, current_admin.id, "delete", "adoption_category", category_id, f"删除认养分类")

    return {"message": "删除成功"}


# ============ 认养配置 ============

@router.get("/configs")
def list_configs(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取认养配置列表"""
    query = db.query(AdoptionConfig)

    if category_id:
        query = query.filter(AdoptionConfig.category_id == category_id)
    if is_active is not None:
        query = query.filter(AdoptionConfig.is_active == is_active)

    configs = query.all()
    return [
        {
            "id": c.id,
            "category_id": c.category_id,
            "category_name": c.category.name if c.category else None,
            "name": c.name,
            "description": c.description,
            "price": c.price,
            "unit": c.unit,
            "duration_days": c.duration_days,
            "benefits": json.loads(c.benefits) if c.benefits else [],
            "images": json.loads(c.images) if c.images else [],
            "is_active": c.is_active,
            "stock": c.stock,
            "created_at": c.created_at
        }
        for c in configs
    ]


@router.get("/configs/{config_id}")
def get_config(
    config_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取认养配置详情"""
    config = db.query(AdoptionConfig).filter(AdoptionConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    return {
        "id": config.id,
        "category_id": config.category_id,
        "category_name": config.category.name if config.category else None,
        "name": config.name,
        "description": config.description,
        "price": config.price,
        "unit": config.unit,
        "duration_days": config.duration_days,
        "benefits": json.loads(config.benefits) if config.benefits else [],
        "images": json.loads(config.images) if config.images else [],
        "is_active": config.is_active,
        "stock": config.stock,
        "created_at": config.created_at
    }


@router.post("/configs")
def create_config(
    category_id: int,
    name: str,
    price: float,
    duration_days: int,
    description: Optional[str] = None,
    unit: str = "year",
    benefits: Optional[str] = None,
    images: Optional[str] = None,
    stock: int = 0,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建认养配置"""
    category = db.query(AdoptionCategory).filter(AdoptionCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    config = AdoptionConfig(
        category_id=category_id,
        name=name,
        price=price,
        duration_days=duration_days,
        description=description,
        unit=unit,
        benefits=benefits,
        images=images,
        stock=stock
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    log_operation(db, current_admin.id, "create", "adoption_config", config.id, f"创建认养配置: {name}")

    return {"id": config.id, "message": "创建成功"}


@router.put("/configs/{config_id}")
def update_config(
    config_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    duration_days: Optional[int] = None,
    description: Optional[str] = None,
    unit: Optional[str] = None,
    benefits: Optional[str] = None,
    images: Optional[str] = None,
    stock: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新认养配置"""
    config = db.query(AdoptionConfig).filter(AdoptionConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    if name:
        config.name = name
    if price is not None:
        config.price = price
    if duration_days is not None:
        config.duration_days = duration_days
    if description:
        config.description = description
    if unit:
        config.unit = unit
    if benefits:
        config.benefits = benefits
    if images:
        config.images = images
    if stock is not None:
        config.stock = stock
    if is_active is not None:
        config.is_active = is_active

    config.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "adoption_config", config_id, f"更新认养配置: {name}")

    return {"message": "更新成功"}


@router.delete("/configs/{config_id}")
def delete_config(
    config_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除认养配置"""
    config = db.query(AdoptionConfig).filter(AdoptionConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 检查是否有订单关联
    orders = db.query(AdoptionOrder).filter(AdoptionOrder.config_id == config_id).count()
    if orders > 0:
        raise HTTPException(status_code=400, detail="该配置下有认养订单，无法删除")

    db.delete(config)
    db.commit()

    log_operation(db, current_admin.id, "delete", "adoption_config", config_id, f"删除认养配置")

    return {"message": "删除成功"}


# ============ 认养订单 ============

@router.get("/orders")
def list_orders(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    config_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取认养订单列表"""
    query = db.query(AdoptionOrder)

    if status:
        query = query.filter(AdoptionOrder.status == status)
    if user_id:
        query = query.filter(AdoptionOrder.user_id == user_id)
    if config_id:
        query = query.filter(AdoptionOrder.config_id == config_id)
    if start_date:
        query = query.filter(func.date(AdoptionOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(AdoptionOrder.created_at) <= end_date)

    total = query.count()
    orders = query.order_by(AdoptionOrder.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_id": o.user_id,
                "user_name": o.user.username if o.user else "未知",
                "config_id": o.config_id,
                "config_name": o.config.name if o.config else "未知",
                "land_parcel_id": o.land_parcel_id,
                "land_parcel_name": o.land_parcel.name if o.land_parcel else None,
                "quantity": o.quantity,
                "total_amount": o.total_amount,
                "status": o.status,
                "start_date": o.start_date,
                "end_date": o.end_date,
                "harvest_info": json.loads(o.harvest_info) if o.harvest_info else None,
                "remark": o.remark,
                "created_at": o.created_at
            }
            for o in orders
        ]
    }


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取认养订单详情"""
    order = db.query(AdoptionOrder).filter(AdoptionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "user_name": order.user.username if order.user else "未知",
        "user_email": order.user.email if order.user else None,
        "config_id": order.config_id,
        "config_name": order.config.name if order.config else "未知",
        "land_parcel_id": order.land_parcel_id,
        "land_parcel_name": order.land_parcel.name if order.land_parcel else None,
        "quantity": order.quantity,
        "total_amount": order.total_amount,
        "status": order.status,
        "start_date": order.start_date,
        "end_date": order.end_date,
        "harvest_info": json.loads(order.harvest_info) if order.harvest_info else None,
        "remark": order.remark,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    remark: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新认养订单状态"""
    order = db.query(AdoptionOrder).filter(AdoptionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    order.status = status
    if remark:
        order.remark = remark

    if status == "active" and order.start_date is None:
        order.start_date = datetime.now()
        if order.config:
            from datetime import timedelta
            order.end_date = datetime.now() + timedelta(days=order.config.duration_days)

    order.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update_status", "adoption_order", order_id, f"更新状态为: {status}")

    return {"message": "状态更新成功"}


@router.put("/orders/{order_id}/allocate")
def allocate_land(
    order_id: int,
    land_parcel_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """为认养订单分配土地"""
    order = db.query(AdoptionOrder).filter(AdoptionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    land = db.query(LandParcel).filter(LandParcel.id == land_parcel_id).first()
    if not land:
        raise HTTPException(status_code=404, detail="土地不存在")

    if land.status != "available":
        raise HTTPException(status_code=400, detail="土地不可用")

    order.land_parcel_id = land_parcel_id
    land.status = "rented"
    order.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "allocate", "adoption_order", order_id, f"分配土地: {land.name}")

    return {"message": "土地分配成功"}
