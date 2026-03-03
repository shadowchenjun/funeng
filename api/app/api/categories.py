"""
分类管理 API - 使用 Supabase
"""
from fastapi import APIRouter, Depends
from app import supabase_client
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_categories():
    """获取所有分类"""
    return supabase_client.get_categories()

@router.get("/{category_id}")
def get_category(category_id: int):
    """获取单个分类"""
    category = supabase_client.get_category_by_id(category_id)
    if not category:
        return {"error": "分类不存在"}
    return category
