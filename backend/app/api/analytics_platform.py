"""
平台级 API - 优化后的慢接口

性能优化点:
1. /export/data     → BackgroundTasks 异步导出，避免 4.2s 阻塞
2. /reports/generate → 批量查询 + 索引优化，替代复杂循环
3. /analytics/summary → 5 分钟 TTL 内存缓存，减少重复计算

路由前缀: /api
"""
import csv
import io
import uuid
import time
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from collections import defaultdict
import os

from app.database import get_db
from app.cache import cached, get_cache, invalidate_cache
from app.models.admin import (
    AdminUser, AdoptionOrder, RentalOrder, LandParcel, Device
)
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.api.admin.auth import get_current_admin

router = APIRouter()

# 导出文件存储目录
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


# ============ 优化 1: 异步导出 /api/export/data ============

class ExportTask:
    """导出任务状态管理 (内存中，生产环境应使用 Redis)"""
    _tasks: dict = {}
    
    @classmethod
    def create(cls, export_type: str) -> str:
        task_id = str(uuid.uuid4())[:8]
        cls._tasks[task_id] = {
            "type": export_type,
            "status": "pending",
            "progress": 0,
            "file_path": None,
            "error": None,
            "created_at": datetime.now().isoformat()
        }
        return task_id
    
    @classmethod
    def update(cls, task_id: str, status: str = None, progress: int = None, file_path: str = None, error: str = None):
        if task_id in cls._tasks:
            if status:
                cls._tasks[task_id]["status"] = status
            if progress is not None:
                cls._tasks[task_id]["progress"] = progress
            if file_path:
                cls._tasks[task_id]["file_path"] = file_path
            if error:
                cls._tasks[task_id]["error"] = error
    
    @classmethod
    def get(cls, task_id: str):
        return cls._tasks.get(task_id)


def _generate_csv(data: List[Dict], filename: str) -> str:
    """生成 CSV 文件并返回路径"""
    if not data:
        return ""
    
    file_path = os.path.join(EXPORT_DIR, f"{filename}.csv")
    
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    return file_path


def _export_worker(db_url: str, task_id: str, export_type: str, filters: dict):
    """
    后台导出任务 (在独立线程中执行，不阻塞主请求)
    
    优化前: 同步导出，API 阻塞 4.2s
    优化后: 后台线程处理，立即返回 task_id
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        ExportTask.update(task_id, status="processing", progress=10)
        
        if export_type == "orders":
            # 导出订单数据 (AdoptionOrder + RentalOrder)
            data = []
            
            # 认养订单
            ExportTask.update(task_id, progress=30)
            adoption_orders = db.query(AdoptionOrder).options(
                joinedload(AdoptionOrder.user),
                joinedload(AdoptionOrder.config)
            ).order_by(AdoptionOrder.created_at.desc()).limit(10000).all()
            
            for o in adoption_orders:
                data.append({
                    "订单类型": "认养订单",
                    "订单号": o.order_no,
                    "用户": o.user.username if o.user else "未知",
                    "配置": o.config.name if o.config else "",
                    "金额": o.total_amount,
                    "状态": o.status,
                    "创建时间": o.created_at.isoformat() if o.created_at else "",
                    "开始日期": o.start_date.isoformat() if o.start_date else "",
                    "结束日期": o.end_date.isoformat() if o.end_date else "",
                })
            
            # 租地订单
            ExportTask.update(task_id, progress=60)
            rental_orders = db.query(RentalOrder).options(
                joinedload(RentalOrder.user),
                joinedload(RentalOrder.land_parcel)
            ).order_by(RentalOrder.created_at.desc()).limit(10000).all()
            
            for o in rental_orders:
                data.append({
                    "订单类型": "租地订单",
                    "订单号": o.order_no,
                    "用户": o.user.username if o.user else "未知",
                    "配置": o.land_parcel.name if o.land_parcel else "",
                    "金额": o.total_amount,
                    "状态": o.status,
                    "创建时间": o.created_at.isoformat() if o.created_at else "",
                    "开始日期": o.start_date.isoformat() if o.start_date else "",
                    "结束日期": o.end_date.isoformat() if o.end_date else "",
                })
            
            ExportTask.update(task_id, progress=80)
            file_path = _generate_csv(data, f"orders_export_{task_id}")
            
        elif export_type == "users":
            # 导出用户数据
            users = db.query(User).order_by(User.created_at.desc()).limit(10000).all()
            data = [{
                "用户名": u.username,
                "邮箱": u.email,
                "活跃状态": "是" if u.is_active else "否",
                "是否管理员": "是" if u.is_admin else "否",
                "创建时间": u.created_at.isoformat() if u.created_at else "",
            } for u in users]
            file_path = _generate_csv(data, f"users_export_{task_id}")
            ExportTask.update(task_id, progress=80)
        
        elif export_type == "products":
            # 导出产品数据
            products = db.query(Product).options(
                joinedload(Product.category)
            ).order_by(Product.created_at.desc()).limit(10000).all()
            data = [{
                "产品名称": p.name,
                "分类": p.category.name if p.category else "未分类",
                "价格": p.price,
                "库存": p.stock,
                "活跃状态": "是" if p.is_active else "否",
                "创建时间": p.created_at.isoformat() if p.created_at else "",
            } for p in products]
            file_path = _generate_csv(data, f"products_export_{task_id}")
            ExportTask.update(task_id, progress=80)
        
        else:
            raise ValueError(f"未知导出类型: {export_type}")
        
        ExportTask.update(task_id, status="completed", progress=100, file_path=file_path)
        
    except Exception as e:
        ExportTask.update(task_id, status="failed", error=str(e))
    finally:
        db.close()


@router.get("/export/data")
def export_data(
    export_type: str = "orders",
    current_admin: AdminUser = Depends(get_current_admin),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    异步数据导出接口
    
    优化前: 同步导出，阻塞 API 4.2s
    优化后: BackgroundTasks 异步处理，立即返回 task_id
    
    支持类型: orders, users, products
    """
    valid_types = ["orders", "users", "products"]
    if export_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"不支持的导出类型，支持: {valid_types}")
    
    task_id = ExportTask.create(export_type)
    
    # 获取数据库 URL 用于后台任务
    db_url = str(db.bind.url)
    
    # 调度后台任务
    background_tasks.add_task(_export_worker, db_url, task_id, export_type, {})
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "导出任务已创建，请在任务完成后使用 /export/status/{task_id} 查询结果"
    }


@router.get("/export/status/{task_id}")
def export_status(task_id: str):
    """查询导出任务状态"""
    task = ExportTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.get("/export/download/{task_id}")
def download_export(
    task_id: str,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """下载导出文件"""
    task = ExportTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"任务未完成，当前状态: {task['status']}")
    
    file_path = task["file_path"]
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    filename = os.path.basename(file_path)
    
    def iterfile():
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk
    
    return StreamingResponse(
        iterfile(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


# ============ 优化 2: 报表生成 /api/reports/generate ============

@router.get("/reports/generate")
def generate_report(
    report_type: str = "overview",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    生成数据报表
    
    优化前: 复杂嵌套循环查询，响应时间 3.5s
    优化后: 批量 GROUP BY 查询 + 索引加速，预期 < 500ms
    
    支持报表类型: overview, adoption, rental, device
    """
    today = datetime.now().date()
    start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else today - timedelta(days=30)
    end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else today
    
    if report_type == "overview":
        # 总览报表 - 使用批量查询替代逐项查询
        # 用户总览
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
        
        # 订单总览
        total_orders = db.query(func.count(AdoptionOrder.id)).scalar() + db.query(func.count(RentalOrder.id)).scalar()
        
        # 收入总览
        adoption_revenue = db.query(func.coalesce(func.sum(AdoptionOrder.total_amount), 0)).filter(
            and_(
                func.date(AdoptionOrder.created_at) >= start,
                func.date(AdoptionOrder.created_at) <= end,
                AdoptionOrder.status.in_(["paid", "active", "completed"])
            )
        ).scalar()
        rental_revenue = db.query(func.coalesce(func.sum(RentalOrder.total_amount), 0)).filter(
            and_(
                func.date(RentalOrder.created_at) >= start,
                func.date(RentalOrder.created_at) <= end,
                RentalOrder.status.in_(["paid", "active", "completed"])
            )
        ).scalar()
        
        # 产品销售排行 (按订单数量) - 修复: AdoptionConfig 与 Product 无关联,直接使用 AdoptionConfig.name
        product_sales = db.query(
            AdoptionConfig.name,
            func.count(AdoptionOrder.id).label("sales_count")
        ).join(
            AdoptionConfig, AdoptionConfig.id == AdoptionOrder.config_id
        ).filter(
            and_(
                func.date(AdoptionOrder.created_at) >= start,
                func.date(AdoptionOrder.created_at) <= end
            )
        ).group_by(AdoptionConfig.name).order_by(func.count(AdoptionOrder.id).desc()).limit(10).all()
        
        # 土地使用率
        total_land = db.query(func.count(LandParcel.id)).scalar()
        rented_land = db.query(func.count(LandParcel.id)).filter(LandParcel.status == "rented").scalar()
        
        land_usage_rate = round(rented_land / total_land * 100, 2) if total_land > 0 else 0
        
        # 设备在线率
        total_devices = db.query(func.count(Device.id)).scalar()
        online_devices = db.query(func.count(Device.id)).filter(Device.status == "online").scalar()
        device_online_rate = round(online_devices / total_devices * 100, 2) if total_devices > 0 else 0
        
        return {
            "report_type": "overview",
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "generated_at": datetime.now().isoformat(),
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "orders": {
                "total": total_orders
            },
            "revenue": {
                "adoption": float(adoption_revenue),
                "rental": float(rental_revenue),
                "total": float(adoption_revenue + rental_revenue)
            },
            "land_usage_rate": land_usage_rate,
            "device_online_rate": device_online_rate,
            "top_products": [{"name": p[0], "sales": p[1]} for p in product_sales]
        }
    
    elif report_type == "adoption":
        # 认养报表 - 按状态分组统计
        status_stats = db.query(
            AdoptionOrder.status,
            func.count(AdoptionOrder.id).label("count"),
            func.coalesce(func.sum(AdoptionOrder.total_amount), 0).label("revenue")
        ).filter(
            and_(
                func.date(AdoptionOrder.created_at) >= start,
                func.date(AdoptionOrder.created_at) <= end
            )
        ).group_by(AdoptionOrder.status).all()
        
        # 每日趋势 (单次 GROUP BY)
        daily_stats = db.query(
            func.date(AdoptionOrder.created_at).label("date"),
            func.count(AdoptionOrder.id).label("count"),
            func.coalesce(func.sum(AdoptionOrder.total_amount), 0).label("revenue")
        ).filter(
            and_(
                func.date(AdoptionOrder.created_at) >= start,
                func.date(AdoptionOrder.created_at) <= end,
                AdoptionOrder.status.in_(["paid", "active", "completed"])
            )
        ).group_by(func.date(AdoptionOrder.created_at)).all()
        
        return {
            "report_type": "adoption",
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "generated_at": datetime.now().isoformat(),
            "by_status": [
                {"status": s, "count": c, "revenue": float(r)}
                for s, c, r in status_stats
            ],
            "daily_trend": [
                {"date": str(row.date), "count": row.count, "revenue": float(row.revenue)}
                for row in daily_stats
            ]
        }
    
    elif report_type == "rental":
        # 租地报表
        status_stats = db.query(
            RentalOrder.status,
            func.count(RentalOrder.id).label("count"),
            func.coalesce(func.sum(RentalOrder.total_amount), 0).label("revenue")
        ).filter(
            and_(
                func.date(RentalOrder.created_at) >= start,
                func.date(RentalOrder.created_at) <= end
            )
        ).group_by(RentalOrder.status).all()
        
        daily_stats = db.query(
            func.date(RentalOrder.created_at).label("date"),
            func.count(RentalOrder.id).label("count"),
            func.coalesce(func.sum(RentalOrder.total_amount), 0).label("revenue")
        ).filter(
            and_(
                func.date(RentalOrder.created_at) >= start,
                func.date(RentalOrder.created_at) <= end,
                RentalOrder.status.in_(["paid", "active", "completed"])
            )
        ).group_by(func.date(RentalOrder.created_at)).all()
        
        return {
            "report_type": "rental",
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "generated_at": datetime.now().isoformat(),
            "by_status": [
                {"status": s, "count": c, "revenue": float(r)}
                for s, c, r in status_stats
            ],
            "daily_trend": [
                {"date": str(row.date), "count": row.count, "revenue": float(row.revenue)}
                for row in daily_stats
            ]
        }
    
    elif report_type == "device":
        # 设备报表
        type_stats = db.query(
            Device.status,
            func.count(Device.id).label("count")
        ).group_by(Device.status).all()
        
        total_devices = db.query(func.count(Device.id)).scalar()
        online = db.query(func.count(Device.id)).filter(Device.status == "online").scalar()
        
        return {
            "report_type": "device",
            "period": {"start": start.isoformat(), "end": end.isoformat()},
            "generated_at": datetime.now().isoformat(),
            "total": total_devices,
            "online": online,
            "offline": total_devices - online,
            "online_rate": round(online / total_devices * 100, 2) if total_devices > 0 else 0,
            "by_status": [{"status": s, "count": c} for s, c in type_stats]
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"不支持的报表类型: {report_type}")


# ============ 优化 3: 分析摘要 /api/analytics/summary (5分钟缓存) ============

from app.models.admin import AdoptionConfig  # 导入避免报表中引用报错


@router.get("/analytics/summary")
def get_analytics_summary(
    force_refresh: bool = False,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    平台分析摘要 (带缓存)
    
    优化前: 每次请求实时聚合，响应 2.8s
    优化后: 5 分钟 TTL 缓存，缓存命中时 < 50ms
    
    查询参数:
    - force_refresh: 强制刷新缓存 (忽略 TTL)
    """
    cache = get_cache()
    cache_key = "analytics:summary:platform"
    
    # 检查缓存 (除非强制刷新)
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            cached_data["_cached"] = True
            return cached_data
    
    # 缓存未命中，执行分析查询
    start_time = time.time()
    
    today = datetime.now().date()
    month_start = today.replace(day=1)
    
    # 1. 用户分析
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    new_users_month = db.query(func.count(User.id)).filter(
        func.date(User.created_at) >= month_start
    ).scalar()
    
    # 2. 订单分析
    adoption_orders_total = db.query(func.count(AdoptionOrder.id)).scalar()
    rental_orders_total = db.query(func.count(RentalOrder.id)).scalar()
    
    adoption_revenue = db.query(func.coalesce(func.sum(AdoptionOrder.total_amount), 0)).filter(
        AdoptionOrder.status.in_(["paid", "active", "completed"])
    ).scalar()
    rental_revenue = db.query(func.coalesce(func.sum(RentalOrder.total_amount), 0)).filter(
        RentalOrder.status.in_(["paid", "active", "completed"])
    ).scalar()
    
    # 3. 本月收入
    month_adoption_rev = db.query(func.coalesce(func.sum(AdoptionOrder.total_amount), 0)).filter(
        and_(
            func.date(AdoptionOrder.created_at) >= month_start,
            AdoptionOrder.status.in_(["paid", "active", "completed"])
        )
    ).scalar()
    month_rental_rev = db.query(func.coalesce(func.sum(RentalOrder.total_amount), 0)).filter(
        and_(
            func.date(RentalOrder.created_at) >= month_start,
            RentalOrder.status.in_(["paid", "active", "completed"])
        )
    ).scalar()
    
    # 4. 土地分析
    total_land = db.query(func.count(LandParcel.id)).scalar()
    rented_land = db.query(func.count(LandParcel.id)).filter(LandParcel.status == "rented").scalar()
    
    # 5. 设备分析
    total_devices = db.query(func.count(Device.id)).scalar()
    online_devices = db.query(func.count(Device.id)).filter(Device.status == "online").scalar()
    
    # 6. 产品分析
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    low_stock_count = db.query(func.count(Product.id)).filter(
        and_(Product.is_active == True, Product.stock < 10)
    ).scalar()
    
    # 7. 用户购买力分析 (有订单的用户占比)
    users_with_orders = db.query(func.count(func.distinct(AdoptionOrder.user_id))).scalar() + \
                        db.query(func.count(func.distinct(RentalOrder.user_id))).scalar()
    purchase_rate = round(users_with_orders / total_users * 100, 2) if total_users > 0 else 0
    
    # 8. 转化率分析 (pending -> paid)
    pending_adoption = db.query(func.count(AdoptionOrder.id)).filter(AdoptionOrder.status == "pending").scalar()
    paid_adoption = db.query(func.count(AdoptionOrder.id)).filter(AdoptionOrder.status == "paid").scalar()
    adoption_conversion = round(paid_adoption / (pending_adoption + paid_adoption) * 100, 2) \
        if (pending_adoption + paid_adoption) > 0 else 0
    
    result = {
        "generated_at": datetime.now().isoformat(),
        "_query_time_ms": round((time.time() - start_time) * 1000, 2),
        "_cached": False,
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "new_this_month": new_users_month,
            "purchase_rate": purchase_rate
        },
        "orders": {
            "adoption_total": adoption_orders_total,
            "rental_total": rental_orders_total,
            "total_revenue": float(adoption_revenue + rental_revenue)
        },
        "revenue": {
            "adoption": float(adoption_revenue),
            "rental": float(rental_revenue),
            "month_adoption": float(month_adoption_rev),
            "month_rental": float(month_rental_rev),
            "month_total": float(month_adoption_rev + month_rental_rev)
        },
        "land": {
            "total": total_land,
            "rented": rented_land,
            "available": total_land - rented_land,
            "utilization_rate": round(rented_land / total_land * 100, 2) if total_land > 0 else 0
        },
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": total_devices - online_devices,
            "online_rate": round(online_devices / total_devices * 100, 2) if total_devices > 0 else 0
        },
        "products": {
            "total": total_products,
            "low_stock": low_stock_count
        },
        "conversion": {
            "adoption_pending": pending_adoption,
            "adoption_paid": paid_adoption,
            "adoption_conversion_rate": adoption_conversion
        }
    }
    
    # 写入缓存 (5 分钟 TTL)
    cache.set(cache_key, result, ttl=300)
    
    return result


@router.delete("/analytics/cache")
def invalidate_analytics_cache(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """手动清除分析缓存"""
    from app.cache import invalidate_cache
    count = invalidate_cache("analytics:*")
    return {"message": f"已清除 {count} 条缓存"}
