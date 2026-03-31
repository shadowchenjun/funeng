"""
简单内存缓存工具 (TTL-based in-memory cache)
用于替代 Redis，对分析摘要等接口进行缓存

注意：此缓存仅适用于单进程场景，进程重启后缓存失效。
生产环境应替换为 Redis。
"""
import time
import threading
from typing import Any, Optional, Callable, Dict, Tuple, List
from functools import wraps


class TTLCache:
    """
    简单的 TTL 缓存实现
    线程安全，支持过期自动清理
    """

    def __init__(self, default_ttl: int = 300):
        """
        default_ttl: 默认过期时间（秒），默认 5 分钟
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.RLock()
        self._default_ttl = default_ttl
        self._cleanup_thread = None

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值，如果不存在或已过期返回 None"""
        with self._lock:
            if key not in self._cache:
                return None
            value, expires_at = self._cache[key]
            if time.time() > expires_at:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值，可指定 TTL"""
        with self._lock:
            ttl = ttl if ttl is not None else self._default_ttl
            expires_at = time.time() + ttl
            self._cache[key] = (value, expires_at)

    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> int:
        """清空所有缓存，返回清空的条目数"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def cleanup_expired(self) -> int:
        """清理所有过期缓存，返回清理的条目数"""
        now = time.time()
        count = 0
        with self._lock:
            expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
            for k in expired_keys:
                del self._cache[k]
                count += 1
        return count

    def keys(self) -> List[str]:
        """返回所有未过期的缓存键"""
        now = time.time()
        with self._lock:
            return [k for k, (_, exp) in self._cache.items() if now <= exp]


# 全局缓存实例 (5 分钟默认 TTL)
_cache = TTLCache(default_ttl=300)


def get_cache() -> TTLCache:
    """获取全局缓存实例"""
    return _cache


def cached(key_prefix: str, ttl: int = 300, key_func: Optional[Callable] = None):
    """
    缓存装饰器

    Args:
        key_prefix: 缓存键前缀
        ttl: 过期时间（秒）
        key_func: 生成缓存键的函数，接收被装饰函数的参数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            if key_func:
                cache_key = "{}:{}".format(key_prefix, key_func(*args, **kwargs))
            else:
                # 使用函数名和参数生成简单键
                import json
                try:
                    params = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
                except Exception:
                    params = str(args) + str(kwargs)
                cache_key = "{}:{}:{}".format(key_prefix, func.__name__, params)

            cache = get_cache()

            # 尝试获取缓存
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # 添加手动清理方法
        wrapper.clear_cache = lambda: get_cache().delete(cache_key) if key_func else None  # noqa: E731
        return wrapper

    return decorator


def invalidate_cache(key_pattern: str = "*") -> int:
    """
    使缓存失效

    Args:
        key_pattern: 键模式，支持 * 通配符
    """
    cache = get_cache()
    if key_pattern == "*":
        return cache.clear()

    # 简单前缀匹配
    count = 0
    keys = cache.keys()
    prefix = key_pattern.rstrip("*")
    for k in keys:
        if k.startswith(prefix):
            if cache.delete(k):
                count += 1
    return count
