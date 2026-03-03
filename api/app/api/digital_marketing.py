"""数字营销 API"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_campaigns():
    return []
