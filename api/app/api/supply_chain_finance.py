"""供应链金融 API"""
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def get_cargo_owners():
    return []
