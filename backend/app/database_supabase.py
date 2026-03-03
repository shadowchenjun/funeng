"""
Supabase 数据库配置
支持 SQLite 本地开发和 Supabase 云端生产环境
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

# Supabase 连接从环境变量获取
SUPABASE_POOL_URL = os.getenv("DATABASE_URL", "")  # Supabase 提供的连接字符串
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# 根据环境选择数据库
def get_database_url():
    """获取数据库连接 URL"""
    # 优先使用 Supabase
    if SUPABASE_POOL_URL:
        return SUPABASE_POOL_URL
    if SUPABASE_URL and "postgresql" in SUPABASE_URL:
        return SUPABASE_URL
    
    # 默认使用 SQLite（本地开发）
    return os.getenv("DATABASE_URL", "sqlite:///./funeng.db")

DATABASE_URL = get_database_url()

# Supabase 使用 PostgreSQL，需要特殊配置
if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # Supabase PostgreSQL 连接
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # Serverless 环境不需要连接池
        connect_args={
            "connect_args": {"connect_timeout": 10}
        }
    )
else:
    # SQLite 本地开发
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
