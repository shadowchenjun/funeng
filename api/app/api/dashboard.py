"""仪表盘 API - 使用 Supabase"""
from fastapi import APIRouter
from app import supabase_client

router = APIRouter()

@router.get("/stats")
def get_stats():
    categories = supabase_client.get_categories()
    products = supabase_client.get_products()
    farm_info = supabase_client.get_farm_info()
    
    return {
        "categories_count": len(categories),
        "products_count": len(products),
        "farm_info": farm_info
    }
