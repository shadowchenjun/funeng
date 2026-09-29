"""
数字营销API - 连接真实数据库
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product as ProductModel
from app.models.smart_agriculture import (
    Member as MemberModel, Campaign as CampaignModel,
    MarketingOrder as MarketingOrderModel, MarketingTrafficDaily as MarketingTrafficModel,
)

router = APIRouter()

# 数据模型统一定义在 app/models/smart_agriculture.py


# ============ Pydantic Schemas ============
class MemberCreate(BaseModel):
    name: str
    phone: str = ""
    level: str = "普通"
    points: int = 0
    total_spent: str = "¥0"
    gender: str = "男"
    birthday: str = ""
    email: str = ""
    address: str = ""
    register_date: str = ""


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    level: Optional[str] = None
    points: Optional[int] = None
    total_spent: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    register_date: Optional[str] = None


class CampaignCreate(BaseModel):
    name: str
    campaign_type: str = "满减活动"
    status: str = "未开始"
    participants: int = 0
    sales: str = "¥0"
    end_date: str = ""


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    campaign_type: Optional[str] = None
    status: Optional[str] = None
    participants: Optional[int] = None
    sales: Optional[str] = None
    end_date: Optional[str] = None


# ============ 会员 API ============
@router.get("/members")
def get_members(db: Session = Depends(get_db)):
    """获取会员列表"""
    members = db.query(MemberModel).all()
    return [{
        "id": m.id,
        "name": m.name,
        "phone": m.phone,
        "level": m.level,
        "points": m.points,
        "totalSpent": m.total_spent,
        "gender": m.gender,
        "birthday": m.birthday,
        "email": m.email,
        "address": m.address,
        "registerDate": m.register_date,
        "createdAt": m.created_at.isoformat() if m.created_at else None
    } for m in members]


@router.post("/members")
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    """创建会员"""
    # 检查手机号是否已存在
    if member.phone:
        existing = db.query(MemberModel).filter(MemberModel.phone == member.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="手机号已被注册")

    new_member = MemberModel(
        name=member.name,
        phone=member.phone,
        level=member.level,
        points=member.points,
        total_spent=member.total_spent,
        gender=member.gender,
        birthday=member.birthday,
        email=member.email,
        address=member.address,
        register_date=member.register_date or datetime.now().strftime("%Y-%m-%d")
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return {"id": new_member.id, "message": "会员创建成功"}


@router.put("/members/{member_id}")
def update_member(member_id: int, member: MemberUpdate, db: Session = Depends(get_db)):
    """更新会员"""
    db_member = db.query(MemberModel).filter(MemberModel.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="会员不存在")

    update_data = member.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_member, key, value)

    db.commit()
    return {"message": "会员更新成功"}


@router.delete("/members/{member_id}")
def delete_member(member_id: int, db: Session = Depends(get_db)):
    """删除会员"""
    db_member = db.query(MemberModel).filter(MemberModel.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="会员不存在")

    db.delete(db_member)
    db.commit()
    return {"message": "会员删除成功"}


@router.get("/members/stats")
def get_member_stats(db: Session = Depends(get_db)):
    """获取会员统计"""
    total = db.query(MemberModel).count()
    by_level = db.query(
        MemberModel.level,
        func.count(MemberModel.id)
    ).group_by(MemberModel.level).all()

    return {
        "total": total,
        "byLevel": {level: count for level, count in by_level}
    }


# ============ 活动 API ============
@router.get("/campaigns")
def get_campaigns(db: Session = Depends(get_db)):
    """获取活动列表"""
    campaigns = db.query(CampaignModel).all()
    return [{
        "id": c.id,
        "name": c.name,
        "type": c.campaign_type,
        "status": c.status,
        "participants": c.participants,
        "sales": c.sales,
        "endDate": c.end_date,
        "createdAt": c.created_at.isoformat() if c.created_at else None
    } for c in campaigns]


@router.post("/campaigns")
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """创建活动"""
    new_campaign = CampaignModel(
        name=campaign.name,
        campaign_type=campaign.campaign_type,
        status=campaign.status,
        participants=campaign.participants,
        sales=campaign.sales,
        end_date=campaign.end_date
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return {"id": new_campaign.id, "message": "活动创建成功"}


@router.put("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    """更新活动"""
    db_campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="活动不存在")

    update_data = campaign.dict(exclude_unset=True)
    # 映射前端字段名到数据库字段名
    field_mapping = {
        "type": "campaign_type",
        "endDate": "end_date"
    }

    for key, value in update_data.items():
        db_key = field_mapping.get(key, key)
        setattr(db_campaign, db_key, value)

    db.commit()
    return {"message": "活动更新成功"}


@router.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """删除活动"""
    db_campaign = db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="活动不存在")

    db.delete(db_campaign)
    db.commit()
    return {"message": "活动删除成功"}


# ============ 电商订单 / 营销分析（来自 marketing_orders / marketing_traffic_daily） ============
PENDING_STATUSES = ("待付款", "待发货")
VALID_STATUSES = ("待付款", "待发货", "配送中", "已完成", "已取消")


def _order_dict(o: MarketingOrderModel) -> dict:
    return {
        "id": o.order_no,
        "order_id": o.id,
        "customer_name": o.customer_name,
        "product": o.product_name,
        "product_id": o.product_id,
        "quantity": o.quantity,
        "unit_price": o.unit_price,
        "price": o.amount,
        "status": o.status,
        "channel": o.channel,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


@router.get("/orders")
def get_orders(status: Optional[str] = None, channel: Optional[str] = None,
               limit: int = Query(20, ge=1, le=500), db: Session = Depends(get_db)):
    """获取电商订单列表（最新在前）"""
    q = db.query(MarketingOrderModel)
    if status:
        q = q.filter(MarketingOrderModel.status == status)
    if channel:
        q = q.filter(MarketingOrderModel.channel == channel)
    orders = q.order_by(MarketingOrderModel.created_at.desc(), MarketingOrderModel.id.desc()).limit(limit).all()
    return [_order_dict(o) for o in orders]


class OrderStatusUpdate(BaseModel):
    status: str


@router.put("/orders/{order_no}/status")
def update_order_status(order_no: str, body: OrderStatusUpdate, db: Session = Depends(get_db)):
    """更新订单状态"""
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="无效的订单状态")
    order = db.query(MarketingOrderModel).filter(MarketingOrderModel.order_no == order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = body.status
    db.commit()
    return _order_dict(order)


def _pct_change(cur: float, prev: float) -> float:
    return round((cur - prev) / prev * 100, 1) if prev else 0.0


@router.get("/analytics")
def get_marketing_analytics(db: Session = Depends(get_db)):
    """获取营销分析数据：概览、今日指标（与昨日对比）、渠道数据"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    valid = MarketingOrderModel.status != "已取消"

    def orders_between(start, end, *filters):
        return db.query(
            func.count(MarketingOrderModel.id), func.coalesce(func.sum(MarketingOrderModel.amount), 0)
        ).filter(MarketingOrderModel.created_at >= start, MarketingOrderModel.created_at < end, valid, *filters).one()

    def traffic(day: datetime):
        return db.query(MarketingTrafficModel).filter(MarketingTrafficModel.date == day.strftime("%Y-%m-%d")).first()

    def new_members(day: datetime) -> int:
        return db.query(MemberModel).filter(MemberModel.register_date == day.strftime("%Y-%m-%d")).count()

    t_count, t_sales = orders_between(today, tomorrow)
    y_count, y_sales = orders_between(yesterday, today)
    t_traffic, y_traffic = traffic(today), traffic(yesterday)
    t_visitors = t_traffic.visitors if t_traffic else 0
    y_visitors = y_traffic.visitors if y_traffic else 0
    t_conv = round(t_count / t_visitors * 100, 2) if t_visitors else 0.0
    y_conv = round(y_count / y_visitors * 100, 2) if y_visitors else 0.0
    t_new, y_new = new_members(today), new_members(yesterday)

    total_orders, total_revenue = db.query(
        func.count(MarketingOrderModel.id), func.coalesce(func.sum(MarketingOrderModel.amount), 0)
    ).filter(valid).one()
    live_count, live_sales = orders_between(today, tomorrow, MarketingOrderModel.channel == "直播间")
    latest_traffic = db.query(MarketingTrafficModel).order_by(MarketingTrafficModel.date.desc()).first()
    push = t_traffic or latest_traffic

    return {
        "overview": {
            "total_members": db.query(MemberModel).count(),
            "total_campaigns": db.query(CampaignModel).count(),
            "total_orders": total_orders,
            "total_revenue": round(float(total_revenue), 2),
        },
        "today": {
            "sales": round(float(t_sales), 2),
            "sales_trend": _pct_change(t_sales, y_sales),
            "orders": t_count,
            "visitors": t_visitors,
            "visitors_trend": _pct_change(t_visitors, y_visitors),
            "conversion_rate": t_conv,
            "conversion_trend": _pct_change(t_conv, y_conv),
            "new_members": t_new,
            "new_members_trend": _pct_change(t_new, y_new),
        },
        "channels": {
            "live": {
                "sessions": t_traffic.live_sessions if t_traffic else 0,
                "orders": live_count,
                "sales": round(float(live_sales), 2),
            },
            "social": {
                "followers": latest_traffic.followers_total if latest_traffic else 0,
                "new_followers": t_traffic.new_followers if t_traffic else 0,
            },
            "ecommerce": {
                "products": db.query(ProductModel).filter(ProductModel.is_active == 1).count(),
                "pending_orders": db.query(MarketingOrderModel).filter(
                    MarketingOrderModel.status.in_(PENDING_STATUSES)).count(),
            },
            "push": {
                "sent": push.push_sent if push else 0,
                "open_rate": round(push.push_opened / push.push_sent * 100, 1) if push and push.push_sent else 0,
            },
        },
    }
