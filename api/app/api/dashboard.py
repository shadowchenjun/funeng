"""
仪表盘API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # 产品总数
    total_products = db.query(func.count(Product.id)).filter(Product.is_active == 1).scalar()
    
    # 分类总数
    total_categories = db.query(func.count(Category.id)).scalar()
    
    # 总库存
    total_stock = db.query(func.sum(Product.stock)).filter(Product.is_active == 1).scalar() or 0
    
    # 产品总价值
    total_value = db.query(func.sum(Product.price * Product.stock)).filter(Product.is_active == 1).scalar() or 0
    
    # 各分类产品数量
    category_stats = db.query(
        Category.name,
        func.count(Product.id).label("count")
    ).outerjoin(Product, Category.id == Product.category_id).group_by(Category.id).all()
    
    return {
        "total_products": total_products,
        "total_categories": total_categories,
        "total_stock": total_stock,
        "total_value": round(total_value, 2),
        "category_stats": [{"name": cat[0], "count": cat[1]} for cat in category_stats]
    }

@router.get("/recent-products")
def get_recent_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active == 1).order_by(Product.created_at.desc()).limit(5).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "created_at": p.created_at.isoformat()
        }
        for p in products
    ]

@router.get("/low-stock-products")
def get_low_stock_products(db: Session = Depends(get_db)):
    """获取库存不足的产品"""
    products = db.query(Product).filter(
        Product.is_active == 1,
        Product.stock < 10
    ).order_by(Product.stock).limit(10).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "category": p.category.name if p.category else "未分类"
        }
        for p in products
    ]
