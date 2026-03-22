"""
营销管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
import json

from app.database import get_db
from app.models.admin import AdminUser, Coupon, Activity
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


# ============ 优惠券 ============

@router.get("/coupons")
def list_coupons(
    is_active: Optional[bool] = None,
    type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取优惠券列表"""
    query = db.query(Coupon)

    if is_active is not None:
        query = query.filter(Coupon.is_active == is_active)
    if type:
        query = query.filter(Coupon.type == type)

    total = query.count()
    coupons = query.order_by(Coupon.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "type": c.type,
                "discount_value": c.discount_value,
                "min_amount": c.min_amount,
                "max_discount": c.max_discount,
                "total_count": c.total_count,
                "used_count": c.used_count,
                "per_user_limit": c.per_user_limit,
                "valid_from": c.valid_from,
                "valid_until": c.valid_until,
                "is_active": c.is_active,
                "created_at": c.created_at
            }
            for c in coupons
        ]
    }


@router.get("/coupons/{coupon_id}")
def get_coupon(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取优惠券详情"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    return {
        "id": coupon.id,
        "name": coupon.name,
        "code": coupon.code,
        "type": coupon.type,
        "discount_value": coupon.discount_value,
        "min_amount": coupon.min_amount,
        "max_discount": coupon.max_discount,
        "total_count": coupon.total_count,
        "used_count": coupon.used_count,
        "per_user_limit": coupon.per_user_limit,
        "valid_from": coupon.valid_from,
        "valid_until": coupon.valid_until,
        "applicable_products": json.loads(coupon.applicable_products) if coupon.applicable_products else None,
        "applicable_categories": json.loads(coupon.applicable_categories) if coupon.applicable_categories else None,
        "is_active": coupon.is_active,
        "created_at": coupon.created_at
    }


@router.post("/coupons")
def create_coupon(
    name: str,
    code: str,
    discount_value: float,
    valid_from: str,
    valid_until: str,
    type: str = "discount",
    min_amount: float = 0,
    max_discount: Optional[float] = None,
    total_count: int = 100,
    per_user_limit: int = 1,
    applicable_products: Optional[str] = None,
    applicable_categories: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建优惠券"""
    existing = db.query(Coupon).filter(Coupon.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="优惠券代码已存在")

    coupon = Coupon(
        name=name,
        code=code,
        type=type,
        discount_value=discount_value,
        min_amount=min_amount,
        max_discount=max_discount,
        total_count=total_count,
        per_user_limit=per_user_limit,
        valid_from=datetime.fromisoformat(valid_from),
        valid_until=datetime.fromisoformat(valid_until),
        applicable_products=applicable_products,
        applicable_categories=applicable_categories
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    log_operation(db, current_admin.id, "create", "coupon", coupon.id, f"创建优惠券: {name}")

    return {"id": coupon.id, "message": "创建成功"}


@router.put("/coupons/{coupon_id}")
def update_coupon(
    coupon_id: int,
    name: Optional[str] = None,
    discount_value: Optional[float] = None,
    valid_from: Optional[str] = None,
    valid_until: Optional[str] = None,
    type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_discount: Optional[float] = None,
    total_count: Optional[int] = None,
    per_user_limit: Optional[int] = None,
    applicable_products: Optional[str] = None,
    applicable_categories: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    if name:
        coupon.name = name
    if discount_value is not None:
        coupon.discount_value = discount_value
    if valid_from:
        coupon.valid_from = datetime.fromisoformat(valid_from)
    if valid_until:
        coupon.valid_until = datetime.fromisoformat(valid_until)
    if type:
        coupon.type = type
    if min_amount is not None:
        coupon.min_amount = min_amount
    if max_discount is not None:
        coupon.max_discount = max_discount
    if total_count is not None:
        coupon.total_count = total_count
    if per_user_limit is not None:
        coupon.per_user_limit = per_user_limit
    if applicable_products:
        coupon.applicable_products = applicable_products
    if applicable_categories:
        coupon.applicable_categories = applicable_categories
    if is_active is not None:
        coupon.is_active = is_active

    coupon.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "coupon", coupon_id, f"更新优惠券: {name}")

    return {"message": "更新成功"}


@router.delete("/coupons/{coupon_id}")
def delete_coupon(
    coupon_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    db.delete(coupon)
    db.commit()

    log_operation(db, current_admin.id, "delete", "coupon", coupon_id, f"删除优惠券")

    return {"message": "删除成功"}


# ============ 活动 ============

@router.get("/activities")
def list_activities(
    status: Optional[str] = None,
    type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取活动列表"""
    query = db.query(Activity)

    if status:
        query = query.filter(Activity.status == status)
    if type:
        query = query.filter(Activity.type == type)

    total = query.count()
    activities = query.order_by(Activity.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "description": a.description,
                "rules": json.loads(a.rules) if a.rules else None,
                "start_time": a.start_time,
                "end_time": a.end_time,
                "status": a.status,
                "banner_url": a.banner_url,
                "created_at": a.created_at
            }
            for a in activities
        ]
    }


@router.get("/activities/{activity_id}")
def get_activity(
    activity_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取活动详情"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    return {
        "id": activity.id,
        "name": activity.name,
        "type": activity.type,
        "description": activity.description,
        "rules": json.loads(activity.rules) if activity.rules else None,
        "start_time": activity.start_time,
        "end_time": activity.end_time,
        "status": activity.status,
        "banner_url": activity.banner_url,
        "created_at": activity.created_at,
        "updated_at": activity.updated_at
    }


@router.post("/activities")
def create_activity(
    name: str,
    type: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    rules: Optional[str] = None,
    banner_url: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建活动"""
    activity = Activity(
        name=name,
        type=type,
        start_time=datetime.fromisoformat(start_time),
        end_time=datetime.fromisoformat(end_time),
        description=description,
        rules=rules,
        banner_url=banner_url
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    log_operation(db, current_admin.id, "create", "activity", activity.id, f"创建活动: {name}")

    return {"id": activity.id, "message": "创建成功"}


@router.put("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    name: Optional[str] = None,
    type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    rules: Optional[str] = None,
    banner_url: Optional[str] = None,
    status: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新活动"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    if name:
        activity.name = name
    if type:
        activity.type = type
    if start_time:
        activity.start_time = datetime.fromisoformat(start_time)
    if end_time:
        activity.end_time = datetime.fromisoformat(end_time)
    if description:
        activity.description = description
    if rules:
        activity.rules = rules
    if banner_url:
        activity.banner_url = banner_url
    if status:
        activity.status = status

    activity.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "activity", activity_id, f"更新活动: {name}")

    return {"message": "更新成功"}


@router.delete("/activities/{activity_id}")
def delete_activity(
    activity_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除活动"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    db.delete(activity)
    db.commit()

    log_operation(db, current_admin.id, "delete", "activity", activity_id, f"删除活动")

    return {"message": "删除成功"}
