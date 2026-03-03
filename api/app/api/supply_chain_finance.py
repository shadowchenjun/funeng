"""供应链金融 API - 使用 Supabase"""
from fastapi import APIRouter
from app import supabase_client

router = APIRouter()

@router.get("/")
def get_cargo_owners():
    """获取货主列表"""
    try:
        result = supabase_client.supabase.table('cargo_owners').select('*').execute()
        return result.data or []
    except Exception as e:
        return {"error": str(e)}

@router.get("/cargo-owners")
def get_cargo_owners_list():
    return get_cargo_owners()
