"""
系统配置API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.models.admin import AdminUser, SystemConfig, AdminOperationLog
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


@router.get("/configs")
def list_configs(
    group: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取系统配置列表"""
    query = db.query(SystemConfig)
    if group:
        query = query.filter(SystemConfig.group == group)

    configs = query.order_by(SystemConfig.group, SystemConfig.id).all()
    return [
        {
            "id": c.id,
            "key": c.key,
            "value": json.loads(c.value) if c.type == "json" else c.value,
            "type": c.type,
            "group": c.group,
            "description": c.description,
            "is_public": c.is_public,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in configs
    ]


@router.get("/configs/{key}")
def get_config(
    key: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取单个配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    return {
        "id": config.id,
        "key": config.key,
        "value": json.loads(config.value) if config.type == "json" else config.value,
        "type": config.type,
        "group": config.group,
        "description": config.description,
        "is_public": config.is_public
    }


@router.put("/configs/{key}")
def update_config(
    key: str,
    value: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    config.value = value
    db.commit()

    log_operation(db, current_admin.id, "update", "system_config", config.id, f"更新配置: {key}")

    return {"message": "更新成功"}


@router.post("/configs")
def create_config(
    key: str,
    value: str,
    type: str = "string",
    group: str = "general",
    description: Optional[str] = None,
    is_public: bool = False,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建系统配置"""
    existing = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if existing:
        raise HTTPException(status_code=400, detail="配置键已存在")

    config = SystemConfig(
        key=key,
        value=value,
        type=type,
        group=group,
        description=description,
        is_public=is_public
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    log_operation(db, current_admin.id, "create", "system_config", config.id, f"创建配置: {key}")

    return {"id": config.id, "message": "创建成功"}


# ============ 操作日志 ============

@router.get("/logs")
def list_operation_logs(
    admin_user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取操作日志"""
    query = db.query(AdminOperationLog)

    if admin_user_id:
        query = query.filter(AdminOperationLog.admin_user_id == admin_user_id)
    if action:
        query = query.filter(AdminOperationLog.action.contains(action))
    if resource:
        query = query.filter(AdminOperationLog.resource == resource)
    if start_date:
        query = query.filter(AdminOperationLog.created_at >= start_date)
    if end_date:
        query = query.filter(AdminOperationLog.created_at <= end_date)

    total = query.count()
    logs = query.order_by(AdminOperationLog.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": log.id,
                "admin_user_id": log.admin_user_id,
                "admin_username": log.admin_user.username if log.admin_user else "未知",
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "detail": log.detail,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }
