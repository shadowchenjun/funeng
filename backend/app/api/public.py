"""
公开接口（无需登录）—— 仅返回聚合统计，不暴露任何明细数据
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdoptionOrder, RentalOrder
from app.models.product import Product
from app.models.user import User

router = APIRouter()

# 计入销售额的订单状态（已付款及之后）
_REVENUE_STATUSES = ("paid", "active", "completed")


@router.get("/stats")
def get_public_stats(db: Session = Depends(get_db)):
    """首页平台概览：注册用户数、订单数、总销售额（元）、在售商品数"""
    order_count = db.query(func.count(AdoptionOrder.id)).scalar() + db.query(func.count(RentalOrder.id)).scalar()
    revenue = (
        db.query(func.coalesce(func.sum(AdoptionOrder.total_amount), 0))
        .filter(AdoptionOrder.status.in_(_REVENUE_STATUSES)).scalar()
        + db.query(func.coalesce(func.sum(RentalOrder.total_amount), 0))
        .filter(RentalOrder.status.in_(_REVENUE_STATUSES)).scalar()
    )
    return {
        "user_count": db.query(func.count(User.id)).scalar(),
        "order_count": order_count,
        "total_revenue": round(float(revenue), 2),
        "product_count": db.query(func.count(Product.id)).filter(Product.is_active == 1).scalar(),
    }
