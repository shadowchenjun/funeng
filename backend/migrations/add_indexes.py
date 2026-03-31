"""
数据库索引迁移脚本
针对慢查询字段添加索引以提升性能

执行方式: python -m migrations.add_indexes
"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal


def add_indexes():
    """为慢查询字段添加数据库索引"""
    db = SessionLocal()
    
    indexes = [
        # adoption_orders 表索引
        ("idx_adoption_orders_status", "adoption_orders", "status"),
        ("idx_adoption_orders_created_at", "adoption_orders", "created_at"),
        ("idx_adoption_orders_user_id", "adoption_orders", "user_id"),
        ("idx_adoption_orders_config_id", "adoption_orders", "config_id"),
        
        # rental_orders 表索引
        ("idx_rental_orders_status", "rental_orders", "status"),
        ("idx_rental_orders_created_at", "rental_orders", "created_at"),
        ("idx_rental_orders_user_id", "rental_orders", "user_id"),
        
        # land_parcels 表索引
        ("idx_land_parcels_status", "land_parcels", "status"),
        
        # devices 表索引
        ("idx_devices_status", "devices", "status"),
        ("idx_devices_land_parcel_id", "devices", "land_parcel_id"),
        
        # users 表索引
        ("idx_users_created_at", "users", "created_at"),
        
        # products 表索引
        ("idx_products_category_id", "products", "category_id"),
        ("idx_products_is_active", "products", "is_active"),
        
        # monitoring_records 表索引 (大数据量表)
        ("idx_monitoring_records_timestamp", "monitoring_records", "timestamp"),
        ("idx_monitoring_records_point_id", "monitoring_records", "monitoring_point_id"),
        
        # device_logs 表索引
        ("idx_device_logs_created_at", "device_logs", "created_at"),
        ("idx_device_logs_device_id", "device_logs", "device_id"),
        
        # admin_operation_logs 表索引
        ("idx_admin_operation_logs_created_at", "admin_operation_logs", "created_at"),
        ("idx_admin_operation_logs_admin_user_id", "admin_operation_logs", "admin_user_id"),
    ]
    
    try:
        for idx_name, table_name, column_name in indexes:
            try:
                # SQLite 语法
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})"
                db.execute(text(sql))
                print(f"✅ 创建索引: {idx_name}")
            except Exception as e:
                print(f"⚠️ 索引 {idx_name} 创建失败: {e}")
        
        db.commit()
        print(f"\n🎉 索引迁移完成! 共创建 {len(indexes)} 个索引")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 迁移失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    add_indexes()
