-- Additive migration: 23 tables defined in ORM but absent from prior migrations.
-- Idempotent; touches no existing table. All new tables enable RLS (backend-only access).
BEGIN;

CREATE TABLE IF NOT EXISTS cold_chain_inbound_appointments (
	id VARCHAR(30) NOT NULL, 
	owner VARCHAR(100) NOT NULL, 
	owner_code VARCHAR(20), 
	vehicle_no VARCHAR(20) NOT NULL, 
	driver VARCHAR(50), 
	driver_phone VARCHAR(20), 
	estimated_arrival TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	actual_arrival TIMESTAMP WITHOUT TIME ZONE, 
	dock VARCHAR(10), 
	zone VARCHAR(50), 
	cargo_type VARCHAR(50), 
	remark VARCHAR(200), 
	items JSON, 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_inbound_appointments" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_inbound_appointments" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_inbound_orders (
	id VARCHAR(30) NOT NULL, 
	appointment_id VARCHAR(30), 
	owner VARCHAR(100) NOT NULL, 
	warehouse VARCHAR(100), 
	inbound_date VARCHAR(10), 
	status VARCHAR(20), 
	dock VARCHAR(10), 
	receiver VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_inbound_orders" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_inbound_orders" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_inventory_alerts (
	id VARCHAR(20) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	level VARCHAR(20) NOT NULL, 
	product VARCHAR(100) NOT NULL, 
	product_code VARCHAR(20), 
	warehouse VARCHAR(100), 
	zone VARCHAR(50), 
	current_value FLOAT NOT NULL, 
	threshold FLOAT NOT NULL, 
	unit VARCHAR(10), 
	status VARCHAR(20), 
	resolve_remark VARCHAR(200), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	resolved_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_inventory_alerts" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_inventory_alerts" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_inventory_rules (
	id VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	enabled BOOLEAN, 
	threshold FLOAT NOT NULL, 
	unit VARCHAR(10), 
	product_categories JSON, 
	notify_channels JSON, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_inventory_rules" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_inventory_rules" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_operating_costs (
	id SERIAL NOT NULL, 
	month VARCHAR(7) NOT NULL, 
	category VARCHAR(20) NOT NULL, 
	amount FLOAT NOT NULL, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_operating_costs" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_operating_costs" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_operation_batches (
	id VARCHAR(30) NOT NULL, 
	zone VARCHAR(20), 
	task_ids JSON NOT NULL, 
	status VARCHAR(10), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_operation_batches" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_operation_batches" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_operation_tasks (
	id VARCHAR(20) NOT NULL, 
	type VARCHAR(10) NOT NULL, 
	priority VARCHAR(10) NOT NULL, 
	status VARCHAR(10), 
	owner VARCHAR(100), 
	location VARCHAR(30), 
	target_location VARCHAR(30), 
	quantity INTEGER NOT NULL, 
	assigned_to VARCHAR(50), 
	assigned_at TIMESTAMP WITHOUT TIME ZONE, 
	started_at TIMESTAMP WITHOUT TIME ZONE, 
	completed_at TIMESTAMP WITHOUT TIME ZONE, 
	barcode VARCHAR(30), 
	error_count INTEGER, 
	batch_id VARCHAR(30), 
	items JSON, 
	history JSON, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_operation_tasks" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_operation_tasks" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_operators (
	employee_id VARCHAR(20) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	department VARCHAR(20) NOT NULL, 
	PRIMARY KEY (employee_id)
);
ALTER TABLE public."cold_chain_operators" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_operators" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_quality_inspections (
	id VARCHAR(20) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	product VARCHAR(100) NOT NULL, 
	batch_no VARCHAR(50) NOT NULL, 
	quantity FLOAT NOT NULL, 
	result VARCHAR(20) NOT NULL, 
	score FLOAT NOT NULL, 
	temperature FLOAT, 
	humidity FLOAT, 
	pesticide_residue FLOAT, 
	heavy_metal FLOAT, 
	inspector VARCHAR(50), 
	location VARCHAR(100), 
	remark VARCHAR(200), 
	items JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_cold_chain_quality_inspections_batch_no ON cold_chain_quality_inspections (batch_no);
ALTER TABLE public."cold_chain_quality_inspections" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_quality_inspections" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_sensors (
	id VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	location VARCHAR(100), 
	kind VARCHAR(10), 
	target_temp FLOAT NOT NULL, 
	tolerance FLOAT, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_sensors" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_sensors" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_temperature_alerts (
	id VARCHAR(20) NOT NULL, 
	sensor_id VARCHAR(20) NOT NULL, 
	location VARCHAR(100), 
	type VARCHAR(20), 
	temperature FLOAT NOT NULL, 
	threshold FLOAT NOT NULL, 
	severity VARCHAR(10) NOT NULL, 
	status VARCHAR(10), 
	message VARCHAR(200), 
	timestamp TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_temperature_alerts" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_temperature_alerts" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_zones (
	id VARCHAR(20) NOT NULL, 
	code VARCHAR(10) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	type VARCHAR(20) NOT NULL, 
	warehouse VARCHAR(100) NOT NULL, 
	owner_code VARCHAR(20), 
	temperature_min FLOAT NOT NULL, 
	temperature_max FLOAT NOT NULL, 
	capacity INTEGER NOT NULL, 
	used INTEGER, 
	distance_to_pick INTEGER, 
	status VARCHAR(20), 
	PRIMARY KEY (id)
);
ALTER TABLE public."cold_chain_zones" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_zones" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS environment_readings (
	id SERIAL NOT NULL, 
	land_id INTEGER, 
	sensor_id VARCHAR(20) NOT NULL, 
	location VARCHAR(100), 
	recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	air_temperature FLOAT, 
	air_humidity FLOAT, 
	wind_speed FLOAT, 
	wind_direction VARCHAR(10), 
	rainfall FLOAT, 
	pressure FLOAT, 
	uv_index FLOAT, 
	visibility FLOAT, 
	light FLOAT, 
	co2 FLOAT, 
	soil_temperature FLOAT, 
	soil_moisture FLOAT, 
	soil_ph FLOAT, 
	nitrogen FLOAT, 
	phosphorus FLOAT, 
	potassium FLOAT, 
	conductivity FLOAT, 
	PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_environment_readings_id ON environment_readings (id);
CREATE INDEX IF NOT EXISTS ix_environment_readings_land_id ON environment_readings (land_id);
CREATE INDEX IF NOT EXISTS ix_environment_readings_recorded_at ON environment_readings (recorded_at);
CREATE INDEX IF NOT EXISTS ix_environment_readings_sensor_id ON environment_readings (sensor_id);
ALTER TABLE public."environment_readings" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."environment_readings" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS irrigation_records (
	id SERIAL NOT NULL, 
	zone_id INTEGER NOT NULL, 
	land_id INTEGER, 
	mode VARCHAR(10), 
	started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	ended_at TIMESTAMP WITHOUT TIME ZONE, 
	duration INTEGER, 
	water_volume FLOAT, 
	moisture_before FLOAT, 
	moisture_after FLOAT, 
	PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_irrigation_records_id ON irrigation_records (id);
CREATE INDEX IF NOT EXISTS ix_irrigation_records_started_at ON irrigation_records (started_at);
CREATE INDEX IF NOT EXISTS ix_irrigation_records_zone_id ON irrigation_records (zone_id);
ALTER TABLE public."irrigation_records" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."irrigation_records" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS irrigation_zones (
	id SERIAL NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	land_id INTEGER, 
	status VARCHAR(20), 
	auto_mode BOOLEAN, 
	rated_flow FLOAT, 
	pressure FLOAT, 
	planned_duration INTEGER, 
	started_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_irrigation_zones_id ON irrigation_zones (id);
CREATE INDEX IF NOT EXISTS ix_irrigation_zones_land_id ON irrigation_zones (land_id);
ALTER TABLE public."irrigation_zones" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."irrigation_zones" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS marketing_orders (
	id SERIAL NOT NULL, 
	order_no VARCHAR(40) NOT NULL, 
	customer_name VARCHAR(50), 
	member_id INTEGER, 
	product_id INTEGER, 
	product_name VARCHAR(200), 
	quantity INTEGER, 
	unit_price FLOAT, 
	amount FLOAT, 
	status VARCHAR(20), 
	channel VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (order_no)
);
CREATE INDEX IF NOT EXISTS ix_marketing_orders_created_at ON marketing_orders (created_at);
CREATE INDEX IF NOT EXISTS ix_marketing_orders_id ON marketing_orders (id);
ALTER TABLE public."marketing_orders" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."marketing_orders" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS marketing_traffic_daily (
	id SERIAL NOT NULL, 
	date VARCHAR(10) NOT NULL, 
	visitors INTEGER, 
	followers_total INTEGER, 
	new_followers INTEGER, 
	push_sent INTEGER, 
	push_opened INTEGER, 
	live_sessions INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (date)
);
CREATE INDEX IF NOT EXISTS ix_marketing_traffic_daily_id ON marketing_traffic_daily (id);
ALTER TABLE public."marketing_traffic_daily" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."marketing_traffic_daily" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS scf_credit_assessments (
	id SERIAL NOT NULL, 
	entity_name VARCHAR(100) NOT NULL, 
	entity_type VARCHAR(20), 
	credit_score INTEGER NOT NULL, 
	level VARCHAR(10) NOT NULL, 
	assessment_date DATE NOT NULL, 
	next_review DATE, 
	factor_financial FLOAT, 
	factor_operation FLOAT, 
	factor_management FLOAT, 
	factor_industry FLOAT, 
	overdue_count INTEGER, 
	debt_ratio FLOAT, 
	cash_flow VARCHAR(10), 
	history JSON, 
	recommendations JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS ix_scf_credit_assessments_id ON scf_credit_assessments (id);
ALTER TABLE public."scf_credit_assessments" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."scf_credit_assessments" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS scf_financing_orders (
	id SERIAL NOT NULL, 
	order_no VARCHAR(50) NOT NULL, 
	applicant VARCHAR(100) NOT NULL, 
	product VARCHAR(100), 
	amount FLOAT NOT NULL, 
	financed_amount FLOAT NOT NULL, 
	rate FLOAT NOT NULL, 
	term INTEGER NOT NULL, 
	status VARCHAR(20), 
	apply_date DATE NOT NULL, 
	expected_return DATE, 
	collateral VARCHAR(50), 
	risk_level VARCHAR(10), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (order_no)
);
CREATE INDEX IF NOT EXISTS ix_scf_financing_orders_id ON scf_financing_orders (id);
CREATE INDEX IF NOT EXISTS ix_scf_financing_orders_status ON scf_financing_orders (status);
ALTER TABLE public."scf_financing_orders" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."scf_financing_orders" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS scf_insurance_policies (
	id SERIAL NOT NULL, 
	policy_no VARCHAR(50) NOT NULL, 
	holder VARCHAR(100) NOT NULL, 
	type VARCHAR(50) NOT NULL, 
	crop VARCHAR(50), 
	area FLOAT, 
	coverage FLOAT NOT NULL, 
	premium FLOAT NOT NULL, 
	deductible FLOAT, 
	start_date DATE NOT NULL, 
	end_date DATE NOT NULL, 
	status VARCHAR(20), 
	claims_count INTEGER, 
	claims_amount FLOAT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (policy_no)
);
CREATE INDEX IF NOT EXISTS ix_scf_insurance_policies_id ON scf_insurance_policies (id);
CREATE INDEX IF NOT EXISTS ix_scf_insurance_policies_status ON scf_insurance_policies (status);
ALTER TABLE public."scf_insurance_policies" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."scf_insurance_policies" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_inbound_order_items (
	id SERIAL NOT NULL, 
	order_id VARCHAR(30) NOT NULL, 
	sku VARCHAR(20) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	barcode VARCHAR(30), 
	storage_type VARCHAR(10) NOT NULL, 
	expected_qty INTEGER NOT NULL, 
	received_qty INTEGER, 
	qualified_qty INTEGER, 
	zone_id VARCHAR(20), 
	location VARCHAR(30), 
	PRIMARY KEY (id), 
	FOREIGN KEY(order_id) REFERENCES cold_chain_inbound_orders (id)
);
CREATE INDEX IF NOT EXISTS ix_cold_chain_inbound_order_items_order_id ON cold_chain_inbound_order_items (order_id);
ALTER TABLE public."cold_chain_inbound_order_items" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_inbound_order_items" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS cold_chain_temperature_readings (
	id SERIAL NOT NULL, 
	sensor_id VARCHAR(20) NOT NULL, 
	temperature FLOAT NOT NULL, 
	humidity FLOAT, 
	recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sensor_id) REFERENCES cold_chain_sensors (id)
);
CREATE INDEX IF NOT EXISTS ix_cold_chain_temperature_readings_recorded_at ON cold_chain_temperature_readings (recorded_at);
CREATE INDEX IF NOT EXISTS ix_cold_chain_temperature_readings_sensor_id ON cold_chain_temperature_readings (sensor_id);
ALTER TABLE public."cold_chain_temperature_readings" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."cold_chain_temperature_readings" FROM anon, authenticated;

CREATE TABLE IF NOT EXISTS scf_receivables (
	id SERIAL NOT NULL, 
	invoice_no VARCHAR(50) NOT NULL, 
	creditor VARCHAR(100) NOT NULL, 
	debtor VARCHAR(100) NOT NULL, 
	amount FLOAT NOT NULL, 
	paid_amount FLOAT, 
	issue_date DATE NOT NULL, 
	due_date DATE NOT NULL, 
	status VARCHAR(20), 
	risk_level VARCHAR(10), 
	financing_order_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (invoice_no), 
	FOREIGN KEY(financing_order_id) REFERENCES scf_financing_orders (id)
);
CREATE INDEX IF NOT EXISTS ix_scf_receivables_id ON scf_receivables (id);
CREATE INDEX IF NOT EXISTS ix_scf_receivables_status ON scf_receivables (status);
ALTER TABLE public."scf_receivables" ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public."scf_receivables" FROM anon, authenticated;

COMMIT;
