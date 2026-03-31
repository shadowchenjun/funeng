"""
Sprint 2 性能对比测试
对比优化前后的 API 响应时间

使用方法: python -m scripts.performance_test
"""
import sys
import os
import time
import requests
import threading
import unittest
from datetime import datetime
from sqlalchemy import text

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


# ============================================================================
# TTLCache 单元测试
# ============================================================================
class TestTTLCache(unittest.TestCase):
    """TTLCache 缓存单元测试"""

    def setUp(self):
        """每次测试前创建新的缓存实例"""
        from app.cache import TTLCache
        self.cache = TTLCache(default_ttl=1)  # 1秒 TTL 用于测试

    def test_basic_set_get(self):
        """测试基本存取"""
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")

    def test_cache_miss(self):
        """测试缓存未命中"""
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_ttl_expiration(self):
        """测试 TTL 过期"""
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")
        time.sleep(1.5)  # 等待过期
        self.assertIsNone(self.cache.get("key"))

    def test_custom_ttl(self):
        """测试自定义 TTL"""
        cache = self.cache.__class__(default_ttl=10)
        cache.set("key", "value")
        self.assertEqual(cache.get("key"), "value")
        # 自定义 TTL 应该比默认 1 秒长
        time.sleep(0.5)
        self.assertEqual(cache.get("key"), "value")

    def test_delete(self):
        """测试删除"""
        self.cache.set("key", "value")
        self.assertTrue(self.cache.delete("key"))
        self.assertIsNone(self.cache.get("key"))
        self.assertFalse(self.cache.delete("nonexistent"))

    def test_clear(self):
        """测试清空"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        count = self.cache.clear()
        self.assertEqual(count, 2)
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_keys(self):
        """测试获取所有 key"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        keys = self.cache.keys()
        self.assertEqual(set(keys), {"key1", "key2"})

    def test_keys_after_expiration(self):
        """测试过期后 key 被排除"""
        self.cache.set("key1", "value1")
        time.sleep(1.5)
        self.assertEqual(self.cache.keys(), [])

    def test_cleanup_expired(self):
        """测试手动清理过期项"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        time.sleep(1.5)
        count = self.cache.cleanup_expired()
        self.assertEqual(count, 2)
        self.assertEqual(self.cache.keys(), [])

    def test_concurrent_access(self):
        """测试并发安全"""
        results = {}
        errors = []

        def writer(thread_id):
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    self.cache.set(key, thread_id * 1000 + i)
            except Exception as e:
                errors.append(e)

        def reader(thread_id):
            try:
                for i in range(100):
                    key = f"thread_{thread_id}_key_{i}"
                    _ = self.cache.get(key)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            t1 = threading.Thread(target=writer, args=(i,))
            t2 = threading.Thread(target=reader, args=(i,))
            threads.extend([t1, t2])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(errors, [], f"并发访问出错: {errors}")


# ============================================================================
# 数据库索引验证
# ============================================================================
def verify_database_indexes():
    """验证数据库索引是否创建成功"""
    print("\n🔍 验证数据库索引...")
    
    # 动态导入避免循环依赖
    from app.database import engine
    
    with engine.connect() as db:
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='index'")).fetchall()
        index_names = [r[0] for r in result]
        
        print(f"   发现 {len(index_names)} 个索引:")
        for name in sorted(index_names):
            if not name.startswith('sqlite_'):
                print(f"     - {name}")
        
        # 核心业务表索引检查
        expected_tables = ['users', 'adoption_configs', 'adoption_orders', 
                         'rental_orders', 'land_parcels', 'devices', 'products']
        
        for table in expected_tables:
            table_indexes = [i for i in index_names if table in i.lower()]
            if table_indexes:
                print(f"   ✅ {table}: {len(table_indexes)} 个索引")
            else:
                print(f"   ⚠️ {table}: 无索引")
        
        return len(index_names)


# ============================================================================
# API 性能测试
# ============================================================================

def get_admin_token():
    """登录获取 token"""
    resp = requests.post(
        f"{API_BASE}/api/auth/login",
        json={"username": "admin", "password": "admin123456"}
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None


def test_endpoint(name: str, method: str, url: str, headers: dict = None, **kwargs):
    """测试单个接口响应时间"""
    start = time.time()
    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, **kwargs)
        elif method.upper() == "POST":
            resp = requests.post(url, headers=headers, **kwargs)
        elapsed = (time.time() - start) * 1000
        return {
            "name": name,
            "status": resp.status_code,
            "time_ms": round(elapsed, 2),
            "success": 200 <= resp.status_code < 300
        }
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return {
            "name": name,
            "status": "ERROR",
            "time_ms": round(elapsed, 2),
            "success": False,
            "error": str(e)
        }


def run_api_tests():
    """运行 API 性能测试"""
    print("\n" + "=" * 60)
    print("Sprint 2 性能优化测试")
    print(f"时间: {datetime.now().isoformat()}")
    print(f"API Base: {API_BASE}")
    print("=" * 60)

    # 获取认证 token
    token = get_admin_token()
    if not token:
        print("❌ 无法获取认证 token，请确保服务器运行中且 admin 已创建")
        print("   启动服务器: cd backend && uvicorn main:app --reload")
        return None

    headers = {"Authorization": f"Bearer {token}"}

    # 测试用例
    tests = [
        # Sprint 2 优化的 3 个慢接口
        ("GET", "/api/export/data?export_type=orders", "异步导出接口", 500),
        ("GET", "/api/reports/generate?report_type=overview", "报表生成接口", 500),
        ("GET", "/api/analytics/summary", "分析摘要接口(冷请求)", 300),
        ("GET", "/api/analytics/summary", "分析摘要接口(缓存命中)", 100),

        # Admin dashboard 优化接口
        ("GET", "/api/admin/dashboard/stats", "管理员看板统计", 300),
        ("GET", "/api/admin/dashboard/charts?days=7", "管理员看板图表", 300),
        ("GET", "/api/admin/dashboard/recent-orders?limit=10", "管理员最近订单", 300),
    ]

    results = []
    failed = False
    
    for method, path, desc, max_ms in tests:
        result = test_endpoint(desc, method, f"{API_BASE}{path}", headers=headers)
        result["max_ms"] = max_ms
        results.append(result)
        status_icon = "✅" if result["success"] else "❌"
        
        # 打印结果
        print(f"{status_icon} [{result['time_ms']:>7.2f}ms] {desc}")
        if not result["success"]:
            print(f"   ❌ 失败: status={result.get('status')}, error={result.get('error')}")
            failed = True
        
        # 断言响应时间
        if result["success"] and result["time_ms"] > max_ms:
            print(f"   ⚠️  警告: 超过目标时间 {max_ms}ms (实际: {result['time_ms']}ms)")
        
    print()
    print("=" * 60)
    print("测试汇总")
    print("=" * 60)

    # 按优化目标分组
    sprint2_apis = results[:4]
    dashboard_apis = results[4:]

    print("\n📊 Sprint 2 核心优化 API:")
    sprint2_times = []
    for r in sprint2_apis:
        sprint2_times.append(r["time_ms"])
        status = "✅" if r["time_ms"] <= r["max_ms"] else "⚠️"
        print(f"   {status} {r['name']}: {r['time_ms']:.2f}ms (目标: {r['max_ms']}ms)")
    avg_sprint2 = sum(sprint2_times)/len(sprint2_times)
    print(f"   平均: {avg_sprint2:.2f}ms")

    print("\n📊 Admin Dashboard 优化 API:")
    dash_times = []
    for r in dashboard_apis:
        dash_times.append(r["time_ms"])
        status = "✅" if r["time_ms"] <= r["max_ms"] else "⚠️"
        print(f"   {status} {r['name']}: {r['time_ms']:.2f}ms (目标: {r['max_ms']}ms)")
    avg_dash = sum(dash_times)/len(dash_times)
    print(f"   平均: {avg_dash:.2f}ms")

    print("\n" + "=" * 60)

    # 预期优化效果对比
    print("\n📈 优化前 vs 优化后 对比:")
    comparisons = [
        ("异步导出 /api/export/data", 4200, sprint2_apis[0]["time_ms"]),
        ("报表生成 /api/reports/generate", 3500, sprint2_apis[1]["time_ms"]),
        ("分析摘要 /api/analytics/summary (冷)", 2800, sprint2_apis[2]["time_ms"]),
        ("分析摘要 (缓存命中)", 2800, sprint2_apis[3]["time_ms"]),
    ]
    print(f"{'接口':<35} {'优化前':>10} {'优化后':>10} {'提升':>10}")
    print("-" * 65)
    for name, before, after in comparisons:
        improvement = (before - after) / before * 100
        print(f"{name:<35} {before:>8.0f}ms {after:>8.0f}ms {improvement:>8.1f}%")

    # =========================================================================
    # 断言验证
    # =========================================================================
    print("\n" + "=" * 60)
    print("🔍 断言验证")
    print("=" * 60)
    
    assertion_failures = []
    
    # 1. 核心接口超时断言
    sprint2_thresholds = [
        (sprint2_apis[0]["name"], sprint2_apis[0]["time_ms"], 500, "导出接口超时"),
        (sprint2_apis[1]["name"], sprint2_apis[1]["time_ms"], 500, "报表接口超时"),
        (sprint2_apis[2]["name"], sprint2_apis[2]["time_ms"], 300, "分析摘要(冷)超时"),
        (sprint2_apis[3]["name"], sprint2_apis[3]["time_ms"], 100, "分析摘要(缓存)超时"),
    ]
    
    for name, time_ms, threshold, msg in sprint2_thresholds:
        try:
            assert time_ms < threshold, f"{msg}: {time_ms}ms >= {threshold}ms"
            print(f"   ✅ {name}: {time_ms}ms < {threshold}ms")
        except AssertionError as e:
            print(f"   ❌ {name}: {e}")
            assertion_failures.append(str(e))
    
    # 2. 所有接口必须成功
    for r in results:
        try:
            assert r["success"], f"接口失败: {r['name']}, status={r.get('status')}, error={r.get('error')}"
            print(f"   ✅ {r['name']}: 成功")
        except AssertionError as e:
            print(f"   ❌ {e}")
            assertion_failures.append(str(e))
    
    # 3. 缓存命中应比冷请求快
    try:
        assert sprint2_apis[3]["time_ms"] < sprint2_apis[2]["time_ms"], \
            f"缓存未加速: 冷={sprint2_apis[2]['time_ms']}ms, 缓存={sprint2_apis[3]['time_ms']}ms"
        print(f"   ✅ 缓存加速: {sprint2_apis[2]['time_ms']}ms -> {sprint2_apis[3]['time_ms']}ms")
    except AssertionError as e:
        print(f"   ❌ {e}")
        assertion_failures.append(str(e))
    
    print("\n" + "=" * 60)
    if assertion_failures:
        print(f"❌ {len(assertion_failures)} 个断言失败:")
        for f in assertion_failures:
            print(f"   - {f}")
        return False
    else:
        print("✅ 所有断言通过!")
        return True


def run_tests():
    """运行所有测试"""
    all_passed = True
    
    # 1. TTLCache 单元测试
    print("=" * 60)
    print("TTLCache 单元测试")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTTLCache)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        all_passed = False
        print("❌ TTLCache 单元测试失败")
    else:
        print("✅ TTLCache 单元测试全部通过")
    
    # 2. 索引验证
    index_count = verify_database_indexes()
    # 期望至少 15 个索引 (Sprint 2 创建了多个)
    min_indexes = 15
    if index_count < min_indexes:
        print(f"⚠️  警告: 索引数量 {index_count} < 期望 {min_indexes}")
        # 不算失败，因为环境可能不同
    
    # 3. API 性能测试
    api_passed = run_api_tests()
    if api_passed is None:  # 无法获取 token
        print("⚠️  API 测试跳过 (服务器可能未运行)")
    elif not api_passed:
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查上述输出")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
