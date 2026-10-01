"""
应用配置 —— 敏感项与部署相关项从环境变量读取

生产环境（Vercel 或 ENVIRONMENT=production）必须提供全部密钥与持久化 Postgres（Supabase），
代码中不设默认值；SQLite 与固定开发密钥仅用于本地开发和测试。
"""
import os
import warnings

IS_PRODUCTION = os.getenv("VERCEL") == "1" or os.getenv("ENVIRONMENT", "").lower() == "production"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./funeng.db")

_DEV_SECRET = "funeng-dev-only-secret-key-change-me-in-prod"
_DEV_ADMIN_SECRET = "funeng-dev-only-admin-secret-key-change-me-in-prod"

# 前台用户与管理员使用不同密钥，避免用户 token 被当作管理员 token 使用
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

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
    if not SECRET_KEY or not ADMIN_SECRET_KEY:
        warnings.warn("SECRET_KEY / ADMIN_SECRET_KEY 未设置，正在使用开发默认值，切勿用于生产环境", stacklevel=1)
    SECRET_KEY = SECRET_KEY or _DEV_SECRET
    ADMIN_SECRET_KEY = ADMIN_SECRET_KEY or _DEV_ADMIN_SECRET

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3001,http://127.0.0.1:3001",
    ).split(",")
    if o.strip()
]
# 允许临时隧道域名（cloudflare / localtunnel），CORSMiddleware 的 allow_origins 不支持通配符
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.(trycloudflare\.com|loca\.lt)")


def sqlite_path() -> str:
    """DATABASE_URL 为 sqlite 时返回数据库文件路径（供少量原生 sqlite3 代码使用）"""
    prefix = "sqlite:///"
    if not DATABASE_URL.startswith(prefix):
        raise RuntimeError("原生 sqlite3 访问仅支持 sqlite DATABASE_URL")
    return DATABASE_URL[len(prefix):]
