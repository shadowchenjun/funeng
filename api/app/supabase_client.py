"""
Supabase 数据库操作 - 使用 Python SDK
"""
import os
from supabase import create_client, Client

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uzxmomyfgkqkbxxkzskc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV6eG1vbXlmZ2txa2J4eGt6c2tjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzExNDA2NzYsImV4cCI6MjA4NjcxNjY3Nn0.fji31Er62NCwVFsCjY-kh8I8xDP0h41_Ujn5d0daAuA")

# 创建全局客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    return supabase

# ==================== User 操作 ====================
def get_user_by_username(username: str):
    result = supabase.table('users').select('*').eq('username', username).execute()
    return result.data[0] if result.data else None

def get_user_by_id(user_id: int):
    result = supabase.table('users').select('*').eq('id', user_id).execute()
    return result.data[0] if result.data else None

def create_user(data: dict):
    result = supabase.table('users').insert(data).execute()
    return result.data[0] if result.data else None

# ==================== Category 操作 ====================
def get_categories():
    result = supabase.table('categories').select('*').execute()
    return result.data or []

def get_category_by_id(category_id: int):
    result = supabase.table('categories').select('*').eq('id', category_id).execute()
    return result.data[0] if result.data else None

# ==================== Product 操作 ====================
def get_products(category_id=None):
    query = supabase.table('products').select('*')
    if category_id:
        query = query.eq('category_id', category_id)
    result = query.execute()
    return result.data or []

def get_product_by_id(product_id: int):
    result = supabase.table('products').select('*').eq('id', product_id).execute()
    return result.data[0] if result.data else None

def create_product(data: dict):
    result = supabase.table('products').insert(data).execute()
    return result.data[0] if result.data else None

def update_product(product_id: int, data: dict):
    result = supabase.table('products').update(data).eq('id', product_id).execute()
    return result.data[0] if result.data else None

def delete_product(product_id: int):
    result = supabase.table('products').delete().eq('id', product_id).execute()
    return result.data

# ==================== Farm 操作 ====================
def get_farm_info():
    result = supabase.table('farm_info').select('*').execute()
    return result.data[0] if result.data else None

def get_lands(farm_id=None):
    query = supabase.table('lands').select('*')
    if farm_id:
        query = query.eq('farm_id', farm_id)
    result = query.execute()
    return result.data or []

def get_crops():
    result = supabase.table('crops').select('*').execute()
    return result.data or []
