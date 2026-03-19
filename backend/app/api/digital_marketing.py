"""
数字营销API - 连接真实数据库
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, func

from app.database import get_db, engine
from app.models.base import Base

router = APIRouter()

# ============ 数据模型 ============
class MemberModel(Base):
    __tablename__ = "members"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    level = Column(String(20), default='普通')
    points = Column(Integer, default=0)
    total_spent = Column(String(50), default='¥0')
    gender = Column(String(10), default='男')
    birthday = Column(String(20))
    email = Column(String(100))
    address = Column(String(200))
    register_date = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class CampaignModel(Base):
    __tablename__ = "campaigns"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    campaign_type = Column(String(50))
    status = Column(String(20), default='未开始')
    participants = Column(Integer, default=0)
    sales = Column(String(50), default='¥0')
    end_date = Column(String(20))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


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


# ============ 保留原有模拟数据接口（用于展示） ============
@router.get("/orders")
def get_orders():
    """获取电商订单列表 - 模拟数据"""
    from datetime import timedelta
    import random

    statuses = ["待付款", "待发货", "配送中", "已完成", "已取消"]
    channels = ["APP", "小程序", "网页", "直播间"]
    products = ["有机大米", "新鲜蔬菜", "水果礼盒", "土特产", "有机水果"]

    orders = []
    for i in range(20):
        date = datetime.now() - timedelta(hours=random.randint(0, 72))
        orders.append({
            "id": f"ORD{datetime.now().strftime('%Y%m%d')}{i+1:04d}",
            "customer_name": f"客户{i+1}",
            "product": random.choice(products),
            "quantity": random.randint(1, 10),
            "price": round(random.uniform(50, 500), 2),
            "status": random.choice(statuses),
            "channel": random.choice(channels),
            "created_at": date.isoformat()
        })
    return orders


@router.get("/analytics")
def get_marketing_analytics(db: Session = Depends(get_db)):
    """获取营销分析数据"""
    member_total = db.query(MemberModel).count()
    campaign_total = db.query(CampaignModel).count()

    return {
        "overview": {
            "total_members": member_total,
            "total_campaigns": campaign_total,
            "total_orders": 0,
            "total_revenue": 0
        }
    }