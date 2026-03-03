"""
Supabase 数据库适配层
将 SQLAlchemy 操作转换为 Supabase SDK 操作
"""
from supabase import Client
from app.database_supabase import get_supabase

class SupabaseDB:
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    # User 操作
    def get_user_by_username(self, username: str):
        result = self.supabase.table('users').select('*').eq('username', username).execute()
        return result.data[0] if result.data else None
    
    def get_user_by_id(self, user_id: int):
        result = self.supabase.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    
    def create_user(self, data: dict):
        result = self.supabase.table('users').insert(data).execute()
        return result.data[0] if result.data else None
    
    # Category 操作
    def get_categories(self):
        result = self.supabase.table('categories').select('*').execute()
        return result.data or []
    
    def get_category_by_id(self, category_id: int):
        result = self.supabase.table('categories').select('*').eq('id', category_id).execute()
        return result.data[0] if result.data else None
    
    # Product 操作
    def get_products(self, category_id=None):
        query = self.supabase.table('products').select('*')
        if category_id:
            query = query.eq('category_id', category_id)
        result = query.execute()
        return result.data or []
    
    def get_product_by_id(self, product_id: int):
        result = self.supabase.table('products').select('*').eq('id', product_id).execute()
        return result.data[0] if result.data else None
    
    # Farm 操作
    def get_farm_info(self):
        result = self.supabase.table('farm_info').select('*').execute()
        return result.data[0] if result.data else None
    
    def get_lands(self, farm_id: int = None):
        query = self.supabase.table('lands').select('*')
        if farm_id:
            query = query.eq('farm_id', farm_id)
        result = query.execute()
        return result.data or []
    
    def get_crops(self):
        result = self.supabase.table('crops').select('*').execute()
        return result.data or []

# 全局数据库实例
_db = None

def get_db():
    global _db
    if _db is None:
        supabase = get_supabase()
        _db = SupabaseDB(supabase)
    return _db
