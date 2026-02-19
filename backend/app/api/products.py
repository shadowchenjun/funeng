"""
产品管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.api.auth import get_current_user

router = APIRouter()

# 获取产品列表
@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(Product.name.contains(search))
    
    products = query.filter(Product.is_active == 1).order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    
    # 添加分类名称
    from app.models.category import Category
    result = []
    for p in products:
        p_dict = {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'unit': p.unit,
            'stock': p.stock,
            'image_url': p.image_url,
            'category_id': p.category_id,
            'origin': p.origin,
            'brand': p.brand,
            'is_active': p.is_active,
            'created_at': p.created_at,
            'updated_at': p.updated_at,
            'category_name': None
        }
        if p.category_id:
            cat = db.query(Category).filter(Category.id == p.category_id).first()
            if cat:
                p_dict['category_name'] = cat.name
        result.append(p_dict)
    
    return result

# 获取单个产品
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product

# 创建产品
@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = Product(**product_data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# 更新产品
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    update_data = product_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

# 删除产品
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    
    # 软删除
    product.is_active = 0
    db.commit()
    return {"message": "产品删除成功"}
