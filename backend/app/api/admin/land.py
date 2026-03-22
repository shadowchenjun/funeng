"""
土地管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.admin import AdminUser, LandParcel, AdoptionOrder, RentalOrder
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


@router.get("/parcels")
def list_parcels(
    status: Optional[str] = None,
    type: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取土地列表"""
    query = db.query(LandParcel)

    if status:
        query = query.filter(LandParcel.status == status)
    if type:
        query = query.filter(LandParcel.type == type)
    if keyword:
        query = query.filter(
            (LandParcel.name.contains(keyword)) |
            (LandParcel.code.contains(keyword)) |
            (LandParcel.location.contains(keyword))
        )

    total = query.count()
    parcels = query.order_by(LandParcel.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "area": p.area,
                "location": p.location,
                "status": p.status,
                "type": p.type,
                "description": p.description,
                "image_url": p.image_url,
                "created_at": p.created_at
            }
            for p in parcels
        ]
    }


@router.get("/parcels/{parcel_id}")
def get_parcel(
    parcel_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取土地详情"""
    parcel = db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="土地不存在")

    # 获取关联的认养订单
    adoption_orders = db.query(AdoptionOrder).filter(
        AdoptionOrder.land_parcel_id == parcel_id,
        AdoptionOrder.status == "active"
    ).all()

    # 获取关联的租地订单
    rental_orders = db.query(RentalOrder).filter(
        RentalOrder.land_parcel_id == parcel_id,
        RentalOrder.status == "active"
    ).all()

    return {
        "id": parcel.id,
        "name": parcel.name,
        "code": parcel.code,
        "area": parcel.area,
        "location": parcel.location,
        "status": parcel.status,
        "type": parcel.type,
        "description": parcel.description,
        "image_url": parcel.image_url,
        "created_at": parcel.created_at,
        "updated_at": parcel.updated_at,
        "adoption_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user": o.user.username if o.user else "未知",
                "end_date": o.end_date
            }
            for o in adoption_orders
        ],
        "rental_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user": o.user.username if o.user else "未知",
                "end_date": o.end_date
            }
            for o in rental_orders
        ]
    }


@router.post("/parcels")
def create_parcel(
    name: str,
    code: str,
    area: float,
    location: Optional[str] = None,
    type: str = "farm",
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建土地"""
    existing = db.query(LandParcel).filter(LandParcel.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="土地编号已存在")

    parcel = LandParcel(
        name=name,
        code=code,
        area=area,
        location=location,
        type=type,
        description=description,
        image_url=image_url
    )
    db.add(parcel)
    db.commit()
    db.refresh(parcel)

    log_operation(db, current_admin.id, "create", "land_parcel", parcel.id, f"创建土地: {name}")

    return {"id": parcel.id, "message": "创建成功"}


@router.put("/parcels/{parcel_id}")
def update_parcel(
    parcel_id: int,
    name: Optional[str] = None,
    area: Optional[float] = None,
    location: Optional[str] = None,
    type: Optional[str] = None,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    status: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新土地"""
    parcel = db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="土地不存在")

    if name:
        parcel.name = name
    if area is not None:
        parcel.area = area
    if location:
        parcel.location = location
    if type:
        parcel.type = type
    if description:
        parcel.description = description
    if image_url:
        parcel.image_url = image_url
    if status:
        parcel.status = status

    parcel.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "land_parcel", parcel_id, f"更新土地: {name}")

    return {"message": "更新成功"}


@router.delete("/parcels/{parcel_id}")
def delete_parcel(
    parcel_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除土地"""
    parcel = db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="土地不存在")

    # 检查是否有活跃的订单
    active_adoption = db.query(AdoptionOrder).filter(
        AdoptionOrder.land_parcel_id == parcel_id,
        AdoptionOrder.status == "active"
    ).count()

    active_rental = db.query(RentalOrder).filter(
        RentalOrder.land_parcel_id == parcel_id,
        RentalOrder.status == "active"
    ).count()

    if active_adoption > 0 or active_rental > 0:
        raise HTTPException(status_code=400, detail="该土地有活跃订单，无法删除")

    db.delete(parcel)
    db.commit()

    log_operation(db, current_admin.id, "delete", "land_parcel", parcel_id, f"删除土地")

    return {"message": "删除成功"}


# ============ 租地订单 ============

@router.get("/rental-orders")
def list_rental_orders(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    land_parcel_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取租地订单列表"""
    query = db.query(RentalOrder)

    if status:
        query = query.filter(RentalOrder.status == status)
    if user_id:
        query = query.filter(RentalOrder.user_id == user_id)
    if land_parcel_id:
        query = query.filter(RentalOrder.land_parcel_id == land_parcel_id)
    if start_date:
        query = query.filter(func.date(RentalOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(RentalOrder.created_at) <= end_date)

    total = query.count()
    orders = query.order_by(RentalOrder.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

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
                "land_parcel_id": o.land_parcel_id,
                "land_parcel_name": o.land_parcel.name if o.land_parcel else "未知",
                "area": o.area,
                "unit_price": o.unit_price,
                "total_amount": o.total_amount,
                "start_date": o.start_date,
                "end_date": o.end_date,
                "status": o.status,
                "crop_plan": o.crop_plan,
                "remark": o.remark,
                "created_at": o.created_at
            }
            for o in orders
        ]
    }


@router.get("/rental-orders/{order_id}")
def get_rental_order(
    order_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取租地订单详情"""
    order = db.query(RentalOrder).filter(RentalOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "user_name": order.user.username if order.user else "未知",
        "user_email": order.user.email if order.user else None,
        "land_parcel_id": order.land_parcel_id,
        "land_parcel_name": order.land_parcel.name if order.land_parcel else "未知",
        "area": order.area,
        "unit_price": order.unit_price,
        "total_amount": order.total_amount,
        "start_date": order.start_date,
        "end_date": order.end_date,
        "status": order.status,
        "crop_plan": order.crop_plan,
        "remark": order.remark,
        "created_at": order.created_at,
        "updated_at": order.updated_at
    }


@router.put("/rental-orders/{order_id}/status")
def update_rental_status(
    order_id: int,
    status: str,
    remark: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新租地订单状态"""
    order = db.query(RentalOrder).filter(RentalOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    old_status = order.status
    order.status = status
    if remark:
        order.remark = remark

    # 如果订单完成或取消，释放土地
    if status in ["completed", "cancelled", "refunded"] and order.land_parcel:
        # 检查是否还有其他活跃订单占用这块土地
        other_active = db.query(RentalOrder).filter(
            RentalOrder.land_parcel_id == order.land_parcel_id,
            RentalOrder.id != order_id,
            RentalOrder.status == "active"
        ).count()

        if other_active == 0:
            order.land_parcel.status = "available"

    order.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update_status", "rental_order", order_id, f"更新状态: {old_status} -> {status}")

    return {"message": "状态更新成功"}
