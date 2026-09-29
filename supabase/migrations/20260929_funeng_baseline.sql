-- Generated baseline for funeng; all application tables require RLS.

CREATE TABLE IF NOT EXISTS activities (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	description TEXT, 
	rules TEXT, 
	start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	status VARCHAR(20), 
	banner_url VARCHAR(500), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_activities_id ON activities (id);
ALTER TABLE public."activities" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS admin_roles (
	id SERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	description TEXT, 
	permissions TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_admin_roles_id ON admin_roles (id);
ALTER TABLE public."admin_roles" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS adoption_categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	icon VARCHAR(50), 
	description TEXT, 
	sort_order INTEGER, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_adoption_categories_id ON adoption_categories (id);
ALTER TABLE public."adoption_categories" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS campaigns (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	campaign_type VARCHAR(50), 
	status VARCHAR(20), 
	participants INTEGER, 
	sales VARCHAR(50), 
	end_date VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_campaigns_id ON campaigns (id);
ALTER TABLE public."campaigns" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS cargo_owners (
	id SERIAL NOT NULL, 
	code VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	contact VARCHAR(50), 
	phone VARCHAR(20), 
	email VARCHAR(100), 
	address VARCHAR(200), 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
ALTER TABLE public."cargo_owners" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	color VARCHAR(20), 
	parent_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (name), 
	FOREIGN KEY(parent_id) REFERENCES categories (id)
)

;
CREATE INDEX IF NOT EXISTS ix_categories_id ON categories (id);
ALTER TABLE public."categories" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS cold_chain_warehouses (
	id VARCHAR NOT NULL, 
	name VARCHAR NOT NULL, 
	address VARCHAR, 
	lat FLOAT, 
	lng FLOAT, 
	capacity FLOAT, 
	used FLOAT, 
	temperature FLOAT, 
	humidity FLOAT, 
	status VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
ALTER TABLE public."cold_chain_warehouses" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS coupons (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	type VARCHAR(20), 
	discount_value FLOAT NOT NULL, 
	min_amount FLOAT, 
	max_discount FLOAT, 
	total_count INTEGER, 
	used_count INTEGER, 
	per_user_limit INTEGER, 
	valid_from TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	valid_until TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	applicable_products TEXT, 
	applicable_categories TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_coupons_id ON coupons (id);
ALTER TABLE public."coupons" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS crop_growth_models (
	id SERIAL NOT NULL, 
	crop_name VARCHAR(100) NOT NULL, 
	crop_type VARCHAR(50), 
	growth_stages TEXT, 
	base_temp FLOAT, 
	optimal_temp_min FLOAT, 
	optimal_temp_max FLOAT, 
	optimal_humidity_min FLOAT, 
	optimal_humidity_max FLOAT, 
	water_requirement FLOAT, 
	fertilizer_requirement FLOAT, 
	expected_yield FLOAT, 
	prediction_accuracy FLOAT, 
	model_version VARCHAR(20), 
	status VARCHAR(20), 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_crop_growth_models_id ON crop_growth_models (id);
ALTER TABLE public."crop_growth_models" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS crops (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	category VARCHAR(50), 
	planting_season VARCHAR(50), 
	growth_days INTEGER, 
	yield_per_mu FLOAT, 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_crops_id ON crops (id);
ALTER TABLE public."crops" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS decision_records (
	id SERIAL NOT NULL, 
	land_id INTEGER, 
	crop_model_id INTEGER, 
	decision_type VARCHAR(50) NOT NULL, 
	current_value FLOAT, 
	recommended_value FLOAT, 
	recommendation TEXT, 
	visualization_data TEXT, 
	confidence FLOAT, 
	executed BOOLEAN, 
	executed_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_decision_records_id ON decision_records (id);
ALTER TABLE public."decision_records" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS device_types (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	icon VARCHAR(50), 
	description TEXT, 
	specifications TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_device_types_id ON device_types (id);
ALTER TABLE public."device_types" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS farm_info (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	address VARCHAR(200), 
	lat FLOAT, 
	lng FLOAT, 
	total_area FLOAT, 
	manager VARCHAR(50), 
	phone VARCHAR(20), 
	coords VARCHAR(50), 
	status VARCHAR(20), 
	description TEXT, 
	established_date VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_farm_info_id ON farm_info (id);
ALTER TABLE public."farm_info" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS iot_devices (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	device_type VARCHAR(50), 
	location VARCHAR(100), 
	land_id INTEGER, 
	status VARCHAR(20), 
	serial_number VARCHAR(100), 
	install_date VARCHAR(20), 
	last_maintenance VARCHAR(20), 
	last_update TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_iot_devices_id ON iot_devices (id);
ALTER TABLE public."iot_devices" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS land_parcels (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	area FLOAT NOT NULL, 
	location VARCHAR(200), 
	status VARCHAR(20), 
	type VARCHAR(20), 
	description TEXT, 
	image_url VARCHAR(500), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_land_parcels_id ON land_parcels (id);
ALTER TABLE public."land_parcels" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS lands (
	id SERIAL NOT NULL, 
	farm_id INTEGER, 
	name VARCHAR(100) NOT NULL, 
	area FLOAT, 
	crop VARCHAR(100), 
	crops TEXT, 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_lands_farm_id ON lands (farm_id);
CREATE INDEX IF NOT EXISTS ix_lands_id ON lands (id);
ALTER TABLE public."lands" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS members (
	id SERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	phone VARCHAR(20), 
	level VARCHAR(20), 
	points INTEGER, 
	total_spent VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	gender VARCHAR(10), 
	birthday VARCHAR(20), 
	email VARCHAR(100), 
	address VARCHAR(200), 
	register_date VARCHAR(20), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_members_id ON members (id);
ALTER TABLE public."members" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS system_configs (
	id SERIAL NOT NULL, 
	key VARCHAR(100) NOT NULL, 
	value TEXT, 
	type VARCHAR(20), 
	"group" VARCHAR(50), 
	description VARCHAR(200), 
	is_public BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (key)
)

;
CREATE INDEX IF NOT EXISTS ix_system_configs_id ON system_configs (id);
ALTER TABLE public."system_configs" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS traceability_chain_nodes (
	id SERIAL NOT NULL, 
	trace_record_id INTEGER NOT NULL, 
	node_type VARCHAR(50) NOT NULL, 
	node_name VARCHAR(100), 
	description TEXT, 
	operator VARCHAR(50), 
	location VARCHAR(200), 
	data TEXT, 
	image_url VARCHAR(200), 
	timestamp VARCHAR(30), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_traceability_chain_nodes_id ON traceability_chain_nodes (id);
ALTER TABLE public."traceability_chain_nodes" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS traceability_records (
	id SERIAL NOT NULL, 
	product_name VARCHAR(100) NOT NULL, 
	product_batch VARCHAR(50), 
	category VARCHAR(50), 
	origin_farm VARCHAR(100), 
	origin_address VARCHAR(200), 
	planting_date VARCHAR(20), 
	harvest_date VARCHAR(20), 
	processing_date VARCHAR(20), 
	processing_factory VARCHAR(100), 
	logistics_company VARCHAR(100), 
	logistics_no VARCHAR(100), 
	warehouse VARCHAR(100), 
	retail_outlet VARCHAR(100), 
	sale_date VARCHAR(20), 
	certifications TEXT, 
	inspection_report TEXT, 
	trace_code VARCHAR(100), 
	qr_code VARCHAR(200), 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (trace_code)
)

;
CREATE INDEX IF NOT EXISTS ix_traceability_records_id ON traceability_records (id);
ALTER TABLE public."traceability_records" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS transports (
	id VARCHAR NOT NULL, 
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
	departure_time TIMESTAMP WITHOUT TIME ZONE, 
	eta TIMESTAMP WITHOUT TIME ZONE, 
	waypoints JSON, 
	route_coords JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_transports_id ON transports (id);
CREATE INDEX IF NOT EXISTS ix_transports_vehicle_no ON transports (vehicle_no);
ALTER TABLE public."transports" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS user_groups (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	description TEXT, 
	criteria TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;
CREATE INDEX IF NOT EXISTS ix_user_groups_id ON user_groups (id);
ALTER TABLE public."user_groups" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS users (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(100), 
	hashed_password VARCHAR(255) NOT NULL, 
	full_name VARCHAR(100), 
	is_active BOOLEAN, 
	is_admin BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users (username);
ALTER TABLE public."users" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS vehicles (
	id SERIAL NOT NULL, 
	plate VARCHAR(20) NOT NULL, 
	vehicle_type VARCHAR(50), 
	driver VARCHAR(50), 
	phone VARCHAR(20), 
	load_capacity FLOAT, 
	volume FLOAT, 
	gps_device VARCHAR(50), 
	temp_range VARCHAR(20), 
	status VARCHAR(20), 
	location VARCHAR(100), 
	temperature FLOAT, 
	battery FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
)

;
ALTER TABLE public."vehicles" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS warehouses (
	id VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	address VARCHAR(200), 
	lat FLOAT, 
	lng FLOAT, 
	capacity FLOAT, 
	used FLOAT, 
	area FLOAT, 
	temperature FLOAT, 
	humidity FLOAT, 
	inventory INTEGER, 
	manager VARCHAR(50), 
	phone VARCHAR(20), 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
)

;
CREATE INDEX IF NOT EXISTS ix_warehouses_id ON warehouses (id);
ALTER TABLE public."warehouses" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS admin_users (
	id SERIAL NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	email VARCHAR(100), 
	hashed_password VARCHAR(255) NOT NULL, 
	full_name VARCHAR(100), 
	phone VARCHAR(20), 
	avatar VARCHAR(500), 
	role_id INTEGER, 
	is_active BOOLEAN, 
	last_login TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(role_id) REFERENCES admin_roles (id)
)

;
CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_users_email ON admin_users (email);
CREATE INDEX IF NOT EXISTS ix_admin_users_id ON admin_users (id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_admin_users_username ON admin_users (username);
ALTER TABLE public."admin_users" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS adoption_configs (
	id SERIAL NOT NULL, 
	category_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	price FLOAT NOT NULL, 
	unit VARCHAR(20), 
	duration_days INTEGER NOT NULL, 
	benefits TEXT, 
	images TEXT, 
	is_active BOOLEAN, 
	stock INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES adoption_categories (id)
)

;
CREATE INDEX IF NOT EXISTS ix_adoption_configs_id ON adoption_configs (id);
ALTER TABLE public."adoption_configs" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS devices (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	device_type_id INTEGER NOT NULL, 
	land_parcel_id INTEGER, 
	location VARCHAR(200), 
	status VARCHAR(20), 
	last_active TIMESTAMP WITHOUT TIME ZONE, 
	config TEXT, 
	firmware_version VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code), 
	FOREIGN KEY(device_type_id) REFERENCES device_types (id), 
	FOREIGN KEY(land_parcel_id) REFERENCES land_parcels (id)
)

;
CREATE INDEX IF NOT EXISTS ix_devices_id ON devices (id);
ALTER TABLE public."devices" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS products (
	id SERIAL NOT NULL, 
	name VARCHAR(200) NOT NULL, 
	description TEXT, 
	price FLOAT NOT NULL, 
	unit VARCHAR(20), 
	stock INTEGER, 
	image_url VARCHAR(500), 
	category_id INTEGER, 
	origin VARCHAR(100), 
	brand VARCHAR(100), 
	is_active INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id)
)

;
CREATE INDEX IF NOT EXISTS ix_products_id ON products (id);
CREATE INDEX IF NOT EXISTS ix_products_name ON products (name);
ALTER TABLE public."products" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS rental_orders (
	id SERIAL NOT NULL, 
	order_no VARCHAR(50) NOT NULL, 
	user_id INTEGER NOT NULL, 
	land_parcel_id INTEGER NOT NULL, 
	area FLOAT NOT NULL, 
	unit_price FLOAT NOT NULL, 
	total_amount FLOAT NOT NULL, 
	start_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	end_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	status VARCHAR(20), 
	crop_plan TEXT, 
	remark TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (order_no), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(land_parcel_id) REFERENCES land_parcels (id)
)

;
CREATE INDEX IF NOT EXISTS ix_rental_orders_id ON rental_orders (id);
ALTER TABLE public."rental_orders" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS traceability_configs (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	description TEXT, 
	land_parcel_id INTEGER, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (code), 
	FOREIGN KEY(land_parcel_id) REFERENCES land_parcels (id)
)

;
CREATE INDEX IF NOT EXISTS ix_traceability_configs_id ON traceability_configs (id);
ALTER TABLE public."traceability_configs" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS uploaded_files (
	filename VARCHAR(100) NOT NULL, 
	owner_id INTEGER, 
	content_type VARCHAR(100) NOT NULL, 
	size INTEGER NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (filename), 
	FOREIGN KEY(owner_id) REFERENCES users (id)
)

;
ALTER TABLE public."uploaded_files" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS admin_operation_logs (
	id SERIAL NOT NULL, 
	admin_user_id INTEGER NOT NULL, 
	action VARCHAR(100) NOT NULL, 
	resource VARCHAR(50) NOT NULL, 
	resource_id INTEGER, 
	detail TEXT, 
	ip_address VARCHAR(50), 
	user_agent TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
)

;
CREATE INDEX IF NOT EXISTS ix_admin_operation_logs_id ON admin_operation_logs (id);
ALTER TABLE public."admin_operation_logs" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS adoption_orders (
	id SERIAL NOT NULL, 
	order_no VARCHAR(50) NOT NULL, 
	user_id INTEGER NOT NULL, 
	config_id INTEGER NOT NULL, 
	land_parcel_id INTEGER, 
	quantity INTEGER, 
	total_amount FLOAT NOT NULL, 
	status VARCHAR(20), 
	start_date TIMESTAMP WITHOUT TIME ZONE, 
	end_date TIMESTAMP WITHOUT TIME ZONE, 
	harvest_info TEXT, 
	remark TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (order_no), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(config_id) REFERENCES adoption_configs (id), 
	FOREIGN KEY(land_parcel_id) REFERENCES land_parcels (id)
)

;
CREATE INDEX IF NOT EXISTS ix_adoption_orders_id ON adoption_orders (id);
ALTER TABLE public."adoption_orders" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS device_logs (
	id SERIAL NOT NULL, 
	device_id INTEGER NOT NULL, 
	log_type VARCHAR(50) NOT NULL, 
	message TEXT NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(device_id) REFERENCES devices (id)
)

;
CREATE INDEX IF NOT EXISTS ix_device_logs_id ON device_logs (id);
ALTER TABLE public."device_logs" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS export_tasks (
	id VARCHAR(36) NOT NULL, 
	admin_user_id INTEGER NOT NULL, 
	export_type VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	progress INTEGER NOT NULL, 
	storage_key VARCHAR(100), 
	error TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(admin_user_id) REFERENCES admin_users (id)
)

;
ALTER TABLE public."export_tasks" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS monitoring_points (
	id SERIAL NOT NULL, 
	device_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	data_type VARCHAR(50) NOT NULL, 
	unit VARCHAR(20), 
	threshold_min FLOAT, 
	threshold_max FLOAT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(device_id) REFERENCES devices (id)
)

;
CREATE INDEX IF NOT EXISTS ix_monitoring_points_id ON monitoring_points (id);
ALTER TABLE public."monitoring_points" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS traceability_nodes (
	id SERIAL NOT NULL, 
	config_id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	node_type VARCHAR(50) NOT NULL, 
	description TEXT, 
	icon VARCHAR(50), 
	sort_order INTEGER, 
	data_fields TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(config_id) REFERENCES traceability_configs (id)
)

;
CREATE INDEX IF NOT EXISTS ix_traceability_nodes_id ON traceability_nodes (id);
ALTER TABLE public."traceability_nodes" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS monitoring_records (
	id SERIAL NOT NULL, 
	monitoring_point_id INTEGER NOT NULL, 
	value FLOAT NOT NULL, 
	timestamp TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(monitoring_point_id) REFERENCES monitoring_points (id)
)

;
CREATE INDEX IF NOT EXISTS ix_monitoring_records_id ON monitoring_records (id);
ALTER TABLE public."monitoring_records" ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS traceability_record_entries (
	id SERIAL NOT NULL, 
	node_id INTEGER NOT NULL, 
	adoption_order_id INTEGER, 
	data TEXT NOT NULL, 
	image_url VARCHAR(500), 
	operator VARCHAR(100), 
	timestamp TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(node_id) REFERENCES traceability_nodes (id), 
	FOREIGN KEY(adoption_order_id) REFERENCES adoption_orders (id)
)

;
CREATE INDEX IF NOT EXISTS ix_traceability_record_entries_id ON traceability_record_entries (id);
ALTER TABLE public."traceability_record_entries" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ADD COLUMN IF NOT EXISTS color VARCHAR(20);
INSERT INTO storage.buckets (id, name, public) VALUES
  ('funeng-images', 'funeng-images', false),
  ('funeng-exports', 'funeng-exports', false)
ON CONFLICT (id) DO NOTHING;
