"""
产品管理 API - 使用 Supabase
"""
from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
from app import supabase_client
from app.api.auth import get_current_user

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: float
    unit: str = ""
    stock: int = 0
    image_url: str = ""
    category_id: Optional[int] = None
    origin: str = ""
    brand: str = ""

@router.get("/")
def get_products(category_id: Optional[int] = None):
    """获取产品列表"""
    return supabase_client.get_products(category_id)

@router.get("/{product_id}")
def get_product(product_id: int):
    """获取单个产品"""
    product = supabase_client.get_product_by_id(product_id)
    if not product:
        return {"error": "产品不存在"}
    return product

@router.post("/")
def create_product(product: ProductCreate, current_user: dict = Depends(get_current_user)):
    """创建产品"""
    data = product.dict()
    if not data.get('image_url'):
        data['image_url'] = ''
    return supabase_client.create_product(data)

@router.put("/{product_id}")
def update_product(product_id: int, product: ProductCreate, current_user: dict = Depends(get_current_user)):
    """更新产品"""
    data = product.dict()
    return supabase_client.update_product(product_id, data)

@router.delete("/{product_id}")
def delete_product(product_id: int, current_user: dict = Depends(get_current_user)):
    """删除产品"""
    return supabase_client.delete_product(product_id)
