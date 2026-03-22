"""
管理员管理API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
import bcrypt

from app.database import get_db
from app.models.admin import AdminUser, AdminRole
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


@router.get("/admins")
def list_admins(
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取管理员列表"""
    query = db.query(AdminUser)

    if role_id:
        query = query.filter(AdminUser.role_id == role_id)
    if is_active is not None:
        query = query.filter(AdminUser.is_active == is_active)
    if keyword:
        query = query.filter(
            (AdminUser.username.contains(keyword)) |
            (AdminUser.full_name.contains(keyword)) |
            (AdminUser.email.contains(keyword))
        )

    total = query.count()
    admins = query.order_by(AdminUser.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": a.id,
                "username": a.username,
                "full_name": a.full_name,
                "email": a.email,
                "phone": a.phone,
                "avatar": a.avatar,
                "role_id": a.role_id,
                "role_name": a.role.name if a.role else None,
                "is_active": a.is_active,
                "last_login": a.last_login,
                "created_at": a.created_at
            }
            for a in admins
        ]
    }


@router.get("/admins/{admin_id}")
def get_admin(
    admin_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取管理员详情"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    return {
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name,
        "email": admin.email,
        "phone": admin.phone,
        "avatar": admin.avatar,
        "role_id": admin.role_id,
        "role_name": admin.role.name if admin.role else None,
        "role_code": admin.role.code if admin.role else None,
        "role_permissions": admin.role.permissions if admin.role else None,
        "is_active": admin.is_active,
        "last_login": admin.last_login,
        "created_at": admin.created_at
    }


@router.post("/admins")
def create_admin(
    username: str,
    password: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    role_id: Optional[int] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建管理员"""
    existing = db.query(AdminUser).filter(AdminUser.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    if email:
        existing_email = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    admin = AdminUser(
        username=username,
        hashed_password=hashed_password,
        email=email,
        full_name=full_name,
        phone=phone,
        role_id=role_id
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    log_operation(db, current_admin.id, "create", "admin_user", admin.id, f"创建管理员: {username}")

    return {"id": admin.id, "message": "创建成功"}


@router.put("/admins/{admin_id}")
def update_admin(
    admin_id: int,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    avatar: Optional[str] = None,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新管理员信息"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if email:
        existing = db.query(AdminUser).filter(AdminUser.email == email, AdminUser.id != admin_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
        admin.email = email
    if full_name:
        admin.full_name = full_name
    if phone:
        admin.phone = phone
    if avatar:
        admin.avatar = avatar
    if role_id is not None:
        admin.role_id = role_id
    if is_active is not None:
        admin.is_active = is_active

    admin.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "admin_user", admin_id, f"更新管理员: {admin.username}")

    return {"message": "更新成功"}


@router.put("/admins/{admin_id}/password")
def reset_password(
    admin_id: int,
    password: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """重置管理员密码"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    admin.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "reset_password", "admin_user", admin_id, f"重置密码: {admin.username}")

    return {"message": "密码重置成功"}


@router.delete("/admins/{admin_id}")
def delete_admin(
    admin_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除管理员"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="管理员不存在")

    if admin.id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    db.delete(admin)
    db.commit()

    log_operation(db, current_admin.id, "delete", "admin_user", admin_id, f"删除管理员")

    return {"message": "删除成功"}


# ============ 角色管理 ============

@router.get("/roles")
def list_roles(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    roles = db.query(AdminRole).order_by(AdminRole.id).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "description": r.description,
            "permissions": r.permissions,
            "is_active": r.is_active,
            "created_at": r.created_at
        }
        for r in roles
    ]


@router.post("/roles")
def create_role(
    name: str,
    code: str,
    description: Optional[str] = None,
    permissions: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建角色"""
    existing = db.query(AdminRole).filter(AdminRole.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="角色代码已存在")

    role = AdminRole(
        name=name,
        code=code,
        description=description,
        permissions=permissions
    )
    db.add(role)
    db.commit()
    db.refresh(role)

    log_operation(db, current_admin.id, "create", "admin_role", role.id, f"创建角色: {name}")

    return {"id": role.id, "message": "创建成功"}


@router.put("/roles/{role_id}")
def update_role(
    role_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    permissions: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新角色"""
    role = db.query(AdminRole).filter(AdminRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if name:
        role.name = name
    if description:
        role.description = description
    if permissions:
        role.permissions = permissions
    if is_active is not None:
        role.is_active = is_active

    role.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "admin_role", role_id, f"更新角色: {name}")

    return {"message": "更新成功"}


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除角色"""
    role = db.query(AdminRole).filter(AdminRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 检查是否有管理员使用该角色
    admins = db.query(AdminUser).filter(AdminUser.role_id == role_id).count()
    if admins > 0:
        raise HTTPException(status_code=400, detail="该角色下有管理员，无法删除")

    db.delete(role)
    db.commit()

    log_operation(db, current_admin.id, "delete", "admin_role", role_id, f"删除角色")

    return {"message": "删除成功"}
