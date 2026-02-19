"""
分类管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithCount
from app.api.auth import get_current_user

router = APIRouter()

# 获取分类列表
@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

# 获取分类列表（带产品数）
@router.get("/with-count", response_model=List[CategoryWithCount])
def get_categories_with_count(
    db: Session = Depends(get_db)
):
    categories = db.query(Category).all()
    result = []
    for cat in categories:
        product_count = len(cat.products) if cat.products else 0
        result.append(CategoryWithCount(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            icon=cat.icon,
            parent_id=cat.parent_id,
            created_at=cat.created_at,
            product_count=product_count
        ))
    return result

# 获取单个分类
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

# 创建分类
@router.post("/", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查分类名是否已存在
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="分类名已存在")
    
    category = Category(**category_data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# 更新分类
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    update_data = category_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    return category

# 删除分类
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    
    # 检查是否有产品关联
    if category.products:
        raise HTTPException(status_code=400, detail="该分类下有产品，无法删除")
    
    db.delete(category)
    db.commit()
    return {"message": "分类删除成功"}
