-- ===============================================
-- 冷链模块数据库更新 SQL
-- 用于线上环境导入
-- ===============================================

-- 1. 创建 transports 运输记录表
CREATE TABLE IF NOT EXISTS transports (
    id VARCHAR NOT NULL PRIMARY KEY,
    vehicle_no VARCHAR NOT NULL,
    driver VARCHAR,
    route VARCHAR,
    start_city VARCHAR,
    end_city VARCHAR,
    status VARCHAR,
    temperature FLOAT,
    humidity FLOAT,
    speed FLOAT,
    fuel FLOAT,
    cargo VARCHAR,
    weight FLOAT,
    current_lat FLOAT,
    current_lng FLOAT,
    current_location VARCHAR,
    departure_time DATETIME,
    eta DATETIME,
    waypoints JSON,
    route_coords JSON,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE INDEX IF NOT EXISTS ix_transports_id ON transports (id);
CREATE INDEX IF NOT EXISTS ix_transports_vehicle_no ON transports (vehicle_no);

-- 2. 创建 vehicles 车辆表
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) DEFAULT '冷藏车',
    driver VARCHAR(50),
    phone VARCHAR(20),
    load_capacity FLOAT DEFAULT 5,
    volume FLOAT,
    gps_device VARCHAR(50),
    temp_range VARCHAR(20) DEFAULT '-25°C~5°C',
    status VARCHAR(20) DEFAULT '空闲',
    location VARCHAR(100),
    temperature FLOAT DEFAULT -18,
    battery FLOAT DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建 cargo_owners 货主表
CREATE TABLE IF NOT EXISTS cargo_owners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address VARCHAR(200),
    status VARCHAR(20) DEFAULT '正常',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. 为 warehouses 表添加缺失的列（如果不存在）
ALTER TABLE warehouses ADD COLUMN area FLOAT;
ALTER TABLE warehouses ADD COLUMN inventory INTEGER DEFAULT 0;
ALTER TABLE warehouses ADD COLUMN manager VARCHAR(50);
ALTER TABLE warehouses ADD COLUMN phone VARCHAR(20);

-- ===============================================
-- 插入运输记录数据
-- ===============================================
INSERT OR REPLACE INTO transports (id, vehicle_no, driver, route, start_city, end_city, status, temperature, humidity, speed, fuel, cargo, weight, current_lat, current_lng, current_location, departure_time, eta, waypoints, route_coords, created_at, updated_at) VALUES
('T0001', '京A12345', '张师傅', '北京-上海', '北京', '上海', 'in_transit', -5.2, 45.0, 85.0, 72.0, '新鲜蔬菜', 15.5, 35.04, 118.78, '济南服务区', '2026-04-01 08:52:37', NULL, '[{"lat": 39.90, "lng": 116.40, "name": "北京"}, {"lat": 36.65, "lng": 117.12, "name": "济南"}, {"lat": 35.04, "lng": 118.78, "name": "临沂"}, {"lat": 32.06, "lng": 118.78, "name": "南京"}, {"lat": 31.23, "lng": 121.47, "name": "上海"}]', '[[116.40, 39.90], [117.12, 36.65], [118.78, 35.04], [118.78, 32.06], [121.47, 31.23]]', '2026-04-01 08:52:37', '2026-04-01 08:52:37'),
('T0002', '京B67890', '李师傅', '广州-成都', '广州', '成都', 'in_transit', 2.5, 55.0, 78.0, 65.0, '新鲜水果', 18.0, 28.22, 112.98, '武汉服务区', '2026-04-01 06:00:00', '2026-04-02 14:00:00', '[{"lat": 23.13, "lng": 113.26, "name": "广州"}, {"lat": 26.58, "lng": 111.32, "name": "桂林"}, {"lat": 28.22, "lng": 112.98, "name": "长沙"}, {"lat": 30.67, "lng": 104.06, "name": "成都"}]', '[[113.26, 23.13], [111.32, 26.58], [112.98, 28.22], [104.06, 30.67]]', '2026-04-01 08:00:00', '2026-04-01 08:00:00'),
('T0003', '津C11111', '王师傅', '武汉-西安', '武汉', '西安', 'in_transit', -3.0, 50.0, 90.0, 80.0, '冷冻食品', 12.0, 34.27, 108.95, '襄阳服务区', '2026-04-01 07:00:00', '2026-04-01 18:00:00', '[{"lat": 30.58, "lng": 114.30, "name": "武汉"}, {"lat": 32.63, "lng": 111.50, "name": "襄阳"}, {"lat": 34.27, "lng": 108.95, "name": "西安"}]', '[[114.30, 30.58], [111.50, 32.63], [108.95, 34.27]]', '2026-04-01 07:00:00', '2026-04-01 07:00:00'),
('T0004', '冀D22222', '刘师傅', '杭州-重庆', '杭州', '重庆', 'waiting', 4.0, 60.0, 0.0, 95.0, '乳制品', 8.0, 30.27, 120.15, '杭州物流园', '2026-04-01 10:00:00', '2026-04-02 20:00:00', '[{"lat": 30.27, "lng": 120.15, "name": "杭州"}, {"lat": 29.56, "lng": 115.98, "name": "南昌"}, {"lat": 29.43, "lng": 106.55, "name": "重庆"}]', '[[120.15, 30.27], [115.98, 29.56], [106.55, 29.43]]', '2026-04-01 09:00:00', '2026-04-01 09:00:00'),
('T0005', '鲁E33333', '陈师傅', '深圳-北京', '深圳', '北京', 'arrived', -18.0, 40.0, 0.0, 30.0, '冷冻肉类', 20.0, 39.9, 116.4, '北京物流中心', '2026-03-31 20:00:00', '2026-04-01 08:00:00', '[{"lat": 22.54, "lng": 114.06, "name": "深圳"}, {"lat": 26.08, "lng": 119.30, "name": "福州"}, {"lat": 29.05, "lng": 120.15, "name": "杭州"}, {"lat": 31.85, "lng": 117.28, "name": "合肥"}, {"lat": 38.03, "lng": 114.48, "name": "石家庄"}, {"lat": 39.90, "lng": 116.40, "name": "北京"}]', '[[114.06, 22.54], [119.30, 26.08], [120.15, 29.05], [117.28, 31.85], [114.48, 38.03], [116.40, 39.90]]', '2026-03-31 20:00:00', '2026-04-01 08:00:00');

-- ===============================================
-- 插入车辆数据
-- ===============================================
INSERT OR REPLACE INTO vehicles (plate, vehicle_type, driver, phone, load_capacity, volume, gps_device, temp_range, status, location, temperature, battery, created_at, updated_at) VALUES
('京A12345', '冷藏车', '张师傅', '13800138001', 5.0, 20.0, 'GPS001', '-25°C~5°C', '运输中', '京津高速', -18.0, 85.0, '2026-04-01 01:53:39', '2026-04-01 01:53:39'),
('京B67890', '冷藏车', '李师傅', '13800138002', 8.0, 30.0, 'GPS002', '-25°C~5°C', '空闲', '北京物流园', -20.0, 92.0, '2026-04-01 01:53:39', '2026-04-01 01:53:39'),
('津C11111', '冷藏车', '王师傅', '13800138003', 5.0, 20.0, 'GPS003', '-25°C~5°C', '运输中', '津沧高速', -15.0, 78.0, '2026-04-01 01:53:39', '2026-04-01 01:53:39'),
('冀D22222', '冷藏车', '刘师傅', '13800138004', 10.0, 40.0, 'GPS004', '-25°C~5°C', '维护中', '石家庄', -18.0, 45.0, '2026-04-01 01:53:39', '2026-04-01 01:53:39'),
('鲁E33333', '冷藏车', '陈师傅', '13800138005', 5.0, 20.0, 'GPS005', '-25°C~5°C', '空闲', '济南中心', -22.0, 100.0, '2026-04-01 01:53:39', '2026-04-01 01:53:39');

-- ===============================================
-- 插入货主数据
-- ===============================================
INSERT OR REPLACE INTO cargo_owners (code, name, contact, phone, email, address, status, created_at) VALUES
('OW1001', '本来生活网', '王总', '13900139001', 'wang@benlai.com', '北京市朝阳区', '正常', '2026-04-01 01:53:39'),
('OW1002', '盒马鲜生', '李总', '13900139002', 'li@hema.com', '上海市浦东新区', '正常', '2026-04-01 01:53:39'),
('OW1003', '永辉超市', '赵总', '13900139003', 'zhao@yonghui.com', '福建省福州市', '正常', '2026-04-01 01:53:39'),
('OW1004', '大润发', '周总', '13900139004', 'zhou@rtmart.com', '江苏省南京市', '正常', '2026-04-01 01:53:39'),
('OW1005', '沃尔玛中国', '吴总', '13900139005', 'wu@walmart.com', '广东省广州市', '正常', '2026-04-01 01:53:39');
