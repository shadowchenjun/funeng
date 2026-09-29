"""Backend deployment configuration.

Production secrets are supplied by the runtime and never have code defaults.
SQLite and fixed development secrets are available only for local development.
"""
import os


IS_PRODUCTION = os.getenv("VERCEL") == "1" or os.getenv("ENVIRONMENT", "").lower() == "production"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./funeng.db")
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
STORAGE_IMAGE_BUCKET = os.getenv("STORAGE_IMAGE_BUCKET", "funeng-images")
STORAGE_EXPORT_BUCKET = os.getenv("STORAGE_EXPORT_BUCKET", "funeng-exports")

if IS_PRODUCTION:
    required = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SECRET_KEY": SECRET_KEY,
        "ADMIN_SECRET_KEY": ADMIN_SECRET_KEY,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_SERVICE_ROLE_KEY,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Missing required production configuration: {', '.join(missing)}")
    if not DATABASE_URL.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        raise RuntimeError("Production DATABASE_URL must use persistent Postgres")
    if not SUPABASE_URL.startswith("https://"):
        raise RuntimeError("Production SUPABASE_URL must use HTTPS")
    if len(SECRET_KEY) < 32 or len(ADMIN_SECRET_KEY) < 32 or SECRET_KEY == ADMIN_SECRET_KEY:
        raise RuntimeError("Production JWT keys must be distinct and at least 32 characters")
else:
    SECRET_KEY = SECRET_KEY or "funeng-local-development-user-key"
    ADMIN_SECRET_KEY = ADMIN_SECRET_KEY or "funeng-local-development-admin-key"

CORS_ORIGINS = [
    item.strip()
    for item in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if item.strip()
]
