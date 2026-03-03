"""数字冷链物联 API - 使用 Supabase"""
from fastapi import APIRouter
from app import supabase_client

router = APIRouter()

@router.get("/")
def get_warehouses():
    """获取仓库列表"""
    try:
        result = supabase_client.supabase.table('warehouses').select('*').execute()
        return result.data or []
    except Exception as e:
        return {"error": str(e)}

@router.get("/warehouses")
def get_warehouses_list():
    return get_warehouses()
