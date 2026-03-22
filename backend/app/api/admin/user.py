"""
用户管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models.admin import AdminUser, UserGroup, AdoptionOrder, RentalOrder
from app.models.user import User
from app.api.admin.auth import get_current_admin

router = APIRouter()


@router.get("/users")
def list_users(
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)

    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.email.contains(keyword))
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if start_date:
        query = query.filter(func.date(User.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(User.created_at) <= end_date)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "created_at": u.created_at
            }
            for u in users
        ]
    }


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户的认养订单
    adoption_orders = db.query(AdoptionOrder).filter(
        AdoptionOrder.user_id == user_id
    ).order_by(AdoptionOrder.created_at.desc()).limit(10).all()

    # 获取用户的租地订单
    rental_orders = db.query(RentalOrder).filter(
        RentalOrder.user_id == user_id
    ).order_by(RentalOrder.created_at.desc()).limit(10).all()

    # 计算用户统计
    total_adoption = db.query(AdoptionOrder).filter(AdoptionOrder.user_id == user_id).count()
    active_adoption = db.query(AdoptionOrder).filter(
        AdoptionOrder.user_id == user_id,
        AdoptionOrder.status == "active"
    ).count()
    total_rental = db.query(RentalOrder).filter(RentalOrder.user_id == user_id).count()
    active_rental = db.query(RentalOrder).filter(
        RentalOrder.user_id == user_id,
        RentalOrder.status == "active"
    ).count()

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "stats": {
            "total_adoption_orders": total_adoption,
            "active_adoption_orders": active_adoption,
            "total_rental_orders": total_rental,
            "active_rental_orders": active_rental
        },
        "adoption_orders": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "config_name": o.config.name if o.config else "未知",
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
                "land_parcel_name": o.land_parcel.name if o.land_parcel else "未知",
                "total_amount": o.total_amount,
                "status": o.status,
                "created_at": o.created_at
            }
            for o in rental_orders
        ]
    }


@router.put("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = is_active
    user.updated_at = datetime.now()
    db.commit()

    return {"message": "状态更新成功"}


# ============ 用户分组 ============

@router.get("/groups")
def list_groups(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户分组列表"""
    groups = db.query(UserGroup).order_by(UserGroup.id).all()
    return [
        {
            "id": g.id,
            "name": g.name,
            "code": g.code,
            "description": g.description,
            "criteria": g.criteria,
            "is_active": g.is_active,
            "created_at": g.created_at
        }
        for g in groups
    ]


@router.post("/groups")
def create_group(
    name: str,
    code: str,
    description: Optional[str] = None,
    criteria: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建用户分组"""
    existing = db.query(UserGroup).filter(UserGroup.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="分组代码已存在")

    group = UserGroup(
        name=name,
        code=code,
        description=description,
        criteria=criteria
    )
    db.add(group)
    db.commit()
    db.refresh(group)

    return {"id": group.id, "message": "创建成功"}


@router.put("/groups/{group_id}")
def update_group(
    group_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    criteria: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户分组"""
    group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")

    if name:
        group.name = name
    if description:
        group.description = description
    if criteria:
        group.criteria = criteria
    if is_active is not None:
        group.is_active = is_active

    group.updated_at = datetime.now()
    db.commit()

    return {"message": "更新成功"}


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除用户分组"""
    group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="分组不存在")

    db.delete(group)
    db.commit()

    return {"message": "删除成功"}
