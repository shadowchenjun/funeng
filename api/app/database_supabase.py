"""
Supabase 配置 - 使用 psycopg2 直接连接（通过 Supabase 的 Transaction Pooler）
"""
import os

# 使用 Supabase Transaction Pooler (端口 6543)
SUPABASE_HOST = os.getenv("SUPABASE_HOST", "db.uzxmomyfgkqkbxxkzskc.supabase.co")
SUPABASE_PORT = os.getenv("SUPABASE_PORT", "6543")  # 使用 Pooler 端口
SUPABASE_USER = os.getenv("SUPABASE_USER", "postgres")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "")  # 从 DATABASE_URL 解析
SUPABASE_DB = os.getenv("SUPABASE_DB", "postgres")

# 从 DATABASE_URL 解析
def get_database_url():
    url = os.getenv("DATABASE_URL", "")
    if url:
        # 替换端口为 6543 (Pooler)
        if "5432" in url:
            url = url.replace("5432", "6543")
        return url
    return f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"

# SQLAlchemy 配置
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 10}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
