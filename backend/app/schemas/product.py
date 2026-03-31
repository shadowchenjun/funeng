"""
产品相关的Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 产品创建
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    unit: str = "kg"
    stock: int = 0
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    origin: Optional[str] = None
    brand: Optional[str] = None

# 产品更新
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    origin: Optional[str] = None
    brand: Optional[str] = None
    is_active: Optional[int] = None

# 产品响应
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    unit: str
    stock: int
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    origin: Optional[str] = None
    brand: Optional[str] = None
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
