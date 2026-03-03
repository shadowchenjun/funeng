"""用户管理 API - 使用 Supabase"""
from fastapi import APIRouter, Depends
from app import supabase_client
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_users(current_user: dict = Depends(get_current_user)):
    """获取用户列表"""
    try:
        result = supabase_client.supabase.table('users').select('*').execute()
        return result.data or []
    except Exception as e:
        return {"error": str(e)}
