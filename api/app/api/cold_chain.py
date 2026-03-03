"""数字冷链物联 API"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_warehouses():
    return []
