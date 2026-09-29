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
from app.schemas.admin import CouponCreate, CouponUpdate, ActivityCreate, ActivityUpdate, apply_update

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
    body: CouponCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建优惠券"""
    existing = db.query(Coupon).filter(Coupon.code == body.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="优惠券代码已存在")

    coupon = Coupon(**body.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)

    log_operation(db, current_admin.id, "create", "coupon", coupon.id, f"创建优惠券: {body.name}")

    return {"id": coupon.id, "message": "创建成功"}


@router.put("/coupons/{coupon_id}")
def update_coupon(
    coupon_id: int,
    body: CouponUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新优惠券"""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="优惠券不存在")

    changes = body.model_dump(exclude_unset=True)
    valid_from = changes.get("valid_from", coupon.valid_from)
    valid_until = changes.get("valid_until", coupon.valid_until)
    if valid_from and valid_until and valid_until <= valid_from:
        raise HTTPException(status_code=422, detail="valid_until 必须晚于 valid_from")

    apply_update(coupon, body)

    coupon.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "coupon", coupon_id, f"更新优惠券: {coupon.name}")

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
    body: ActivityCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建活动"""
    activity = Activity(**body.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)

    log_operation(db, current_admin.id, "create", "activity", activity.id, f"创建活动: {body.name}")

    return {"id": activity.id, "message": "创建成功"}


@router.put("/activities/{activity_id}")
def update_activity(
    activity_id: int,
    body: ActivityUpdate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新活动"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")

    changes = body.model_dump(exclude_unset=True)
    start_time = changes.get("start_time", activity.start_time)
    end_time = changes.get("end_time", activity.end_time)
    if start_time and end_time and end_time <= start_time:
        raise HTTPException(status_code=422, detail="end_time 必须晚于 start_time")

    apply_update(activity, body)

    activity.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "activity", activity_id, f"更新活动: {activity.name}")

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
