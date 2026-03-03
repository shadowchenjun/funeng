-- Funeng Database Export for Supabase (PostgreSQL)

-- Tables
CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(50) NOT NULL UNIQUE, email VARCHAR(100) UNIQUE, hashed_password VARCHAR(255) NOT NULL, full_name VARCHAR(100), is_active BOOLEAN DEFAULT true, is_admin BOOLEAN DEFAULT false, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE categories (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL UNIQUE, description TEXT, icon VARCHAR(50), parent_id INTEGER REFERENCES categories(id), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE lands (id SERIAL PRIMARY KEY, farm_id INTEGER, name VARCHAR(100) NOT NULL, area FLOAT, crop VARCHAR(100), crops TEXT, status VARCHAR(20) DEFAULT 'normal', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE crops (id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, category VARCHAR(50), planting_season VARCHAR(50), growth_days INTEGER, yield_per_mu FLOAT, status VARCHAR(20) DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE farm_info (id SERIAL PRIMARY KEY, name VARCHAR(200), address VARCHAR(200), lat FLOAT, lng FLOAT, total_area FLOAT, manager VARCHAR(50), phone VARCHAR(20), coords VARCHAR(50), status VARCHAR(20) DEFAULT 'normal', description TEXT, established_date VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE products (id SERIAL PRIMARY KEY, name VARCHAR(200) NOT NULL, description TEXT, price FLOAT NOT NULL, unit VARCHAR(20), stock INTEGER DEFAULT 0, image_url VARCHAR(500), category_id INTEGER REFERENCES categories(id), origin VARCHAR(100), brand VARCHAR(100), is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- Data (password: test123456)
INSERT INTO users (username, email, hashed_password, full_name, is_active, is_admin) VALUES ('johnnychenjun', 'johnnychenjun@test.com', '$2b$12$dW/7T2OFGWciZzkhrOHp4.SQDEqC.1LTm4t2L9fJMqlXDSGoA1quy', '', true, true);

INSERT INTO categories (name, description, icon) VALUES ('新鲜蔬菜', '新鲜采摘的蔬菜', '🥬');
INSERT INTO categories (name, description, icon) VALUES ('新鲜水果', '新鲜水果', '🍎');
INSERT INTO categories (name, description, icon) VALUES ('土特产', '地方特产', '🎁');
INSERT INTO categories (name, description, icon) VALUES ('肉禽蛋', '新鲜肉类和禽蛋', '🥩');
INSERT INTO categories (name, description, icon) VALUES ('粮油米面', '粮食和食用油', '🌾');

INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('有机西红柿', '优质有机西红柿，产地直销', 12.8, 'kg', 100, 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400', 1);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('新鲜黄瓜', '优质新鲜黄瓜，产地直销', 8.5, 'kg', 150, 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=400', 1);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('有机生菜', '优质有机生菜，产地直销', 6.0, 'kg', 80, 'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400', 1);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('红富士苹果', '优质红富士苹果，产地直销', 15.0, 'kg', 200, 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400', 2);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('新鲜草莓', '优质新鲜草莓，产地直销', 35.0, 'kg', 50, 'https://images.unsplash.com/photo-1518635017498-87f514b751ba?w=400', 2);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('赣南脐橙', '优质赣南脐橙，产地直销', 18.0, 'kg', 120, 'https://images.unsplash.com/photo-1547514701-42782101795e?w=400', 2);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('农家腊肉', '优质农家腊肉，产地直销', 68.0, 'kg', 30, 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=400', 3);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('高山茶叶', '优质高山茶叶，产地直销', 128.0, 'kg', 25, 'https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400', 3);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('土鸡蛋', '优质土鸡蛋，产地直销', 2.5, 'kg', 500, 'https://images.unsplash.com/photo-1516467508483-a7212febe31a?w=400', 4);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('新鲜猪肉', '优质新鲜猪肉，产地直销', 32.0, 'kg', 80, 'https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400', 4);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('东北大米', '优质东北大米，产地直销', 55.0, 'kg', 200, 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400', 5);
INSERT INTO products (name, description, price, unit, stock, image_url, category_id) VALUES ('花生油', '优质花生油，产地直销', 45.0, 'kg', 60, 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400', 5);

INSERT INTO farm_info (name, address, lat, lng, total_area, manager, phone, coords, status, description, established_date) VALUES ('智慧生态农场', '山东省济南市历城区', 36.65, 117.12, 120.0, '张建国', '138****8888', '36.65°N, 117.12°E', 'normal', '专注于有机农业的现代化农场', '2020-01-01');

INSERT INTO lands (farm_id, name, area, crop, crops, status) VALUES (1, 'A区大棚1', 15.0, '西红柿', '西红柿,黄瓜', 'normal');
INSERT INTO lands (farm_id, name, area, crop, crops, status) VALUES (1, 'B区大棚2', 20.0, '黄瓜', '黄瓜,茄子', 'normal');
INSERT INTO lands (farm_id, name, area, crop, crops, status) VALUES (1, 'C区露天', 30.0, '小麦', '小麦,玉米', 'normal');
INSERT INTO lands (farm_id, name, area, crop, crops, status) VALUES (1, 'D区露天', 25.0, '玉米', '玉米,大豆', 'normal');

INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('小麦', '粮食', '秋季', 240, 800.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('玉米', '粮食', '春季', 120, 1000.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('水稻', '粮食', '夏季', 150, 1200.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('西红柿', '蔬菜', '春季', 90, 5000.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('黄瓜', '蔬菜', '春季', 60, 4000.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('茄子', '蔬菜', '春季', 80, 3500.0, 'active');
INSERT INTO crops (name, category, planting_season, growth_days, yield_per_mu, status) VALUES ('大豆', '粮食', '夏季', 100, 300.0, 'active');
