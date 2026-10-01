"""
数据库配置
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import DATABASE_URL

engine_options = {}
if DATABASE_URL.startswith("sqlite:"):
    engine_options["connect_args"] = {"check_same_thread": False}
else:
    # Supabase's transaction pooler handles connection reuse for serverless callers.
    engine_options["poolclass"] = NullPool
    engine_options["connect_args"] = {"prepare_threshold": None}
    for scheme in ("postgres://", "postgresql://"):
        if DATABASE_URL.startswith(scheme):
            DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len(scheme):]
            break

engine = create_engine(DATABASE_URL, **engine_options)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
