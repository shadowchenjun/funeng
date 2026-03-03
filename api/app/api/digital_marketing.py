"""数字营销 API - 使用 Supabase"""
from fastapi import APIRouter
from app import supabase_client

router = APIRouter()

@router.get("/")
def get_campaigns():
    """获取营销活动列表"""
    try:
        result = supabase_client.supabase.table('campaigns').select('*').execute()
        return result.data or []
    except Exception as e:
        return {"error": str(e)}

@router.get("/campaigns")
def get_campaigns_list():
    return get_campaigns()
