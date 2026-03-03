"""用户管理 API"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_users():
    return []
