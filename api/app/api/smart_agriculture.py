"""智慧农业 API - 使用 Supabase"""
from fastapi import APIRouter, Depends
from app import supabase_client
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/farm-info")
def get_farm_info():
    return supabase_client.get_farm_info() or {}

@router.get("/lands")
def get_lands(farm_id: int = None):
    return supabase_client.get_lands(farm_id)

@router.get("/crops")
def get_crops():
    return supabase_client.get_crops()
