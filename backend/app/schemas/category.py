"""
分类相关的Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 分类创建
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None

# 分类更新
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None

# 分类响应
class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

# 带产品数的分类响应
class CategoryWithCount(CategoryResponse):
    product_count: int = 0
