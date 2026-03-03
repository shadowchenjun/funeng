"""Supabase 客户端 - 使用 Python SDK"""
import os
import sys

# 打印环境变量调试
print(f"[Supabase] URL: {os.getenv('SUPABASE_URL', 'NOT SET')}", file=sys.stderr)
print(f"[Supabase] KEY: {os.getenv('SUPABASE_KEY', 'NOT SET')[:20]}...", file=sys.stderr)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uzxmomyfgkqkbxxkzskc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_KEY:
    print("[Supabase] ⚠️ 未配置 SUPABASE_KEY", file=sys.stderr)

try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[Supabase] ✅ SDK 初始化成功", file=sys.stderr)
except Exception as e:
    print(f"[Supabase] ❌ 初始化失败: {e}", file=sys.stderr)
    supabase = None

# 辅助函数：安全获取 data
def get_data(result):
    """安全获取 Supabase 返回的 data"""
    if not result:
        return []
    if hasattr(result, 'data') and result.data is not None:
        return result.data
    return []

# ==================== Users 操作 ====================
def authenticate_user(username: str, password: str):
    if not supabase:
        return None
    result = supabase.table('users').select('*').eq('username', username).execute()
    users = get_data(result)
    if not users:
        return None
    user = users[0]
    if user.get('password') == password:
        return user
    return None

def get_user_by_id(user_id: int):
    if not supabase:
        return None
    result = supabase.table('users').select('*').eq('id', user_id).execute()
    users = get_data(result)
    return users[0] if users else None

def get_user_by_username(username: str):
    if not supabase:
        return None
    result = supabase.table('users').select('*').eq('username', username).execute()
    users = get_data(result)
    return users[0] if users else None

def create_user(data: dict):
    if not supabase:
        return None
    result = supabase.table('users').insert(data).execute()
    items = get_data(result)
    return items[0] if items else None

# ==================== Categories 操作 ====================
def get_categories():
    if not supabase:
        return []
    result = supabase.table('categories').select('*').order('id').execute()
    return get_data(result)

def get_category_by_id(category_id: int):
    if not supabase:
        return None
    result = supabase.table('categories').select('*').eq('id', category_id).execute()
    categories = get_data(result)
    return categories[0] if categories else None

def create_category(data: dict):
    if not supabase:
        return None
    result = supabase.table('categories').insert(data).execute()
    items = get_data(result)
    return items[0] if items else None

def update_category(category_id: int, data: dict):
    if not supabase:
        return None
    result = supabase.table('categories').update(data).eq('id', category_id).execute()
    items = get_data(result)
    return items[0] if items else None

def delete_category(category_id: int):
    if not supabase:
        return False
    result = supabase.table('categories').delete().eq('id', category_id).execute()
    return True

# ==================== Products 操作 ====================
def get_products(category_id=None):
    if not supabase:
        return []
    query = supabase.table('products').select('*, categories(name)').order('id')
    if category_id:
        query = query.eq('category_id', category_id)
    result = query.execute()
    items = get_data(result)
    for item in items:
        if 'categories' in item and item['categories']:
            item['category_name'] = item['categories'].get('name')
        item.pop('categories', None)
    return items

def get_product_by_id(product_id: int):
    if not supabase:
        return None
    result = supabase.table('products').select('*, categories(name)').eq('id', product_id).execute()
    items = get_data(result)
    if items:
        item = items[0]
        if 'categories' in item and item['categories']:
            item['category_name'] = item['categories'].get('name')
        item.pop('categories', None)
        return item
    return None

def create_product(data: dict):
    if not supabase:
        return None
    result = supabase.table('products').insert(data).execute()
    items = get_data(result)
    return items[0] if items else None

def update_product(product_id: int, data: dict):
    if not supabase:
        return None
    result = supabase.table('products').update(data).eq('id', product_id).execute()
    items = get_data(result)
    return items[0] if items else None

def delete_product(product_id: int):
    if not supabase:
        return False
    result = supabase.table('products').delete().eq('id', product_id).execute()
    return True

# ==================== Farm 操作 ====================
def get_farm_info():
    if not supabase:
        return None
    result = supabase.table('farm_info').select('*').execute()
    items = get_data(result)
    return items[0] if items else None

def get_lands(farm_id=None):
    if not supabase:
        return []
    query = supabase.table('lands').select('*')
    if farm_id:
        query = query.eq('farm_id', farm_id)
    result = query.execute()
    return get_data(result)

def get_crops(land_id=None):
    if not supabase:
        return []
    query = supabase.table('crops').select('*')
    if land_id:
        query = query.eq('land_id', land_id)
    result = query.execute()
    return get_data(result)

# ==================== Dashboard Stats ====================
def get_dashboard_stats():
    if not supabase:
        return {"products": 0, "categories": 0, "orders": 0, "users": 0}
    
    products = get_data(supabase.table('products').select('id', count='exact').execute())
    categories = get_data(supabase.table('categories').select('id', count='exact').execute())
    
    return {
        "products": len(products) if products else 0,
        "categories": len(categories) if categories else 0,
        "orders": 0,
        "users": 1
    }
