"""
溯源管理API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
import json

from app.database import get_db
from app.models.admin import (
    AdminUser, TraceabilityConfig, TraceabilityNode, TraceabilityRecordEntry
)
from app.api.admin.auth import get_current_admin, log_operation

router = APIRouter()


# ============ 溯源配置 ============

@router.get("/configs")
def list_configs(
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取溯源配置列表"""
    query = db.query(TraceabilityConfig)
    if is_active is not None:
        query = query.filter(TraceabilityConfig.is_active == is_active)

    configs = query.order_by(TraceabilityConfig.id).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "description": c.description,
            "land_parcel_id": c.land_parcel_id,
            "land_parcel_name": c.land_parcel.name if c.land_parcel else None,
            "is_active": c.is_active,
            "created_at": c.created_at
        }
        for c in configs
    ]


@router.post("/configs")
def create_config(
    name: str,
    code: str,
    description: Optional[str] = None,
    land_parcel_id: Optional[int] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建溯源配置"""
    existing = db.query(TraceabilityConfig).filter(TraceabilityConfig.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="配置代码已存在")

    config = TraceabilityConfig(
        name=name,
        code=code,
        description=description,
        land_parcel_id=land_parcel_id
    )
    db.add(config)
    db.commit()
    db.refresh(config)

    log_operation(db, current_admin.id, "create", "traceability_config", config.id, f"创建溯源配置: {name}")

    return {"id": config.id, "message": "创建成功"}


@router.put("/configs/{config_id}")
def update_config(
    config_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    land_parcel_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新溯源配置"""
    config = db.query(TraceabilityConfig).filter(TraceabilityConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    if name:
        config.name = name
    if description:
        config.description = description
    if land_parcel_id is not None:
        config.land_parcel_id = land_parcel_id
    if is_active is not None:
        config.is_active = is_active

    config.updated_at = datetime.now()
    db.commit()

    log_operation(db, current_admin.id, "update", "traceability_config", config_id, f"更新溯源配置: {name}")

    return {"message": "更新成功"}


# ============ 溯源节点 ============

@router.get("/configs/{config_id}/nodes")
def list_nodes(
    config_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取溯源节点列表"""
    nodes = db.query(TraceabilityNode).filter(
        TraceabilityNode.config_id == config_id
    ).order_by(TraceabilityNode.sort_order).all()

    return [
        {
            "id": n.id,
            "config_id": n.config_id,
            "name": n.name,
            "node_type": n.node_type,
            "description": n.description,
            "icon": n.icon,
            "sort_order": n.sort_order,
            "data_fields": json.loads(n.data_fields) if n.data_fields else [],
            "is_active": n.is_active,
            "created_at": n.created_at
        }
        for n in nodes
    ]


@router.post("/nodes")
def create_node(
    config_id: int,
    name: str,
    node_type: str,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: int = 0,
    data_fields: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建溯源节点"""
    config = db.query(TraceabilityConfig).filter(TraceabilityConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    node = TraceabilityNode(
        config_id=config_id,
        name=name,
        node_type=node_type,
        icon=icon,
        description=description,
        sort_order=sort_order,
        data_fields=data_fields
    )
    db.add(node)
    db.commit()
    db.refresh(node)

    log_operation(db, current_admin.id, "create", "traceability_node", node.id, f"创建溯源节点: {name}")

    return {"id": node.id, "message": "创建成功"}


@router.put("/nodes/{node_id}")
def update_node(
    node_id: int,
    name: Optional[str] = None,
    node_type: Optional[str] = None,
    icon: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: Optional[int] = None,
    data_fields: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新溯源节点"""
    node = db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    if name:
        node.name = name
    if node_type:
        node.node_type = node_type
    if icon:
        node.icon = icon
    if description:
        node.description = description
    if sort_order is not None:
        node.sort_order = sort_order
    if data_fields:
        node.data_fields = data_fields
    if is_active is not None:
        node.is_active = is_active

    db.commit()

    log_operation(db, current_admin.id, "update", "traceability_node", node_id, f"更新溯源节点: {name}")

    return {"message": "更新成功"}


@router.delete("/nodes/{node_id}")
def delete_node(
    node_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除溯源节点"""
    node = db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    db.query(TraceabilityRecordEntry).filter(TraceabilityRecordEntry.node_id == node_id).delete()
    db.delete(node)
    db.commit()

    log_operation(db, current_admin.id, "delete", "traceability_node", node_id, f"删除溯源节点")

    return {"message": "删除成功"}


# ============ 溯源记录 ============

@router.get("/records")
def list_records(
    node_id: Optional[int] = None,
    adoption_order_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取溯源记录列表"""
    query = db.query(TraceabilityRecordEntry)

    if node_id:
        query = query.filter(TraceabilityRecordEntry.node_id == node_id)
    if adoption_order_id:
        query = query.filter(TraceabilityRecordEntry.adoption_order_id == adoption_order_id)
    if start_date:
        query = query.filter(func.date(TraceabilityRecordEntry.timestamp) >= start_date)
    if end_date:
        query = query.filter(func.date(TraceabilityRecordEntry.timestamp) <= end_date)

    total = query.count()
    records = query.order_by(TraceabilityRecordEntry.timestamp.desc()).offset((page-1)*page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "node_id": r.node_id,
                "node_name": r.node.name if r.node else None,
                "adoption_order_id": r.adoption_order_id,
                "order_no": r.adoption_order.order_no if r.adoption_order else None,
                "data": json.loads(r.data) if r.data else {},
                "image_url": r.image_url,
                "operator": r.operator,
                "timestamp": r.timestamp,
                "created_at": r.created_at
            }
            for r in records
        ]
    }


@router.post("/records")
def create_record(
    node_id: int,
    data: str,
    adoption_order_id: Optional[int] = None,
    image_url: Optional[str] = None,
    operator: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """创建溯源记录"""
    node = db.query(TraceabilityNode).filter(TraceabilityNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")

    record = TraceabilityRecordEntry(
        node_id=node_id,
        adoption_order_id=adoption_order_id,
        data=data,
        image_url=image_url,
        operator=operator or current_admin.full_name or current_admin.username
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_operation(db, current_admin.id, "create", "traceability_record", record.id, f"创建溯源记录")

    return {"id": record.id, "message": "创建成功"}


@router.get("/records/{record_id}")
def get_record(
    record_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取溯源记录详情"""
    record = db.query(TraceabilityRecordEntry).filter(TraceabilityRecordEntry.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return {
        "id": record.id,
        "node_id": record.node_id,
        "node_name": record.node.name if record.node else None,
        "adoption_order_id": record.adoption_order_id,
        "order_no": record.adoption_order.order_no if record.adoption_order else None,
        "data": json.loads(record.data) if record.data else {},
        "image_url": record.image_url,
        "operator": record.operator,
        "timestamp": record.timestamp,
        "created_at": record.created_at
    }
