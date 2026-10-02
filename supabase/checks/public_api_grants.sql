-- 只读核查：收回 Data API 权限迁移的执行前 / 执行后对比（r3，按「有效权限」检查）
-- 每段结果独立，可在 SQL Editor 中整体执行，保存两次输出对比。
-- 本文件不依赖快照表，首次迁移前也可完整执行；快照核查另见 public_api_snapshot.sql（仅执行后）。

-- [1] funeng 目标表：anon/authenticated 的有效权限（含 PUBLIC、继承角色、列级）。执行后应全部为 false
WITH targets AS (
  SELECT c.oid, c.relname FROM pg_class c
  WHERE c.relnamespace = 'public'::regnamespace AND c.relkind IN ('r','p','v','m','f')
    AND c.relname = ANY (ARRAY[
    'agri_collection_runs',
    'activities', 'admin_operation_logs', 'admin_roles', 'admin_users', 'adoption_categories',
    'adoption_configs', 'adoption_orders', 'agri_data_import_runs', 'agri_data_sources', 'campaigns',
    'cargo_owners', 'categories', 'cold_chain_inbound_appointments', 'cold_chain_inbound_order_items', 'cold_chain_inbound_orders',
    'cold_chain_inventory_alerts', 'cold_chain_inventory_rules', 'cold_chain_operating_costs', 'cold_chain_operation_batches', 'cold_chain_operation_tasks',
    'cold_chain_operators', 'cold_chain_quality_inspections', 'cold_chain_reference_nodes', 'cold_chain_sensors', 'cold_chain_temperature_alerts',
    'cold_chain_temperature_readings', 'cold_chain_warehouses', 'cold_chain_zones', 'coupons', 'crop_growth_models',
    'crops', 'decision_records', 'device_logs', 'device_types', 'devices',
    'environment_readings', 'export_tasks', 'farm_info', 'funeng_migration_conflicts', 'industry_observations',
    'iot_devices', 'irrigation_records', 'irrigation_zones', 'land_parcels', 'lands',
    'market_price_observations', 'marketing_orders', 'marketing_traffic_daily', 'members', 'monitoring_points',
    'monitoring_records', 'products', 'rental_orders', 'scf_credit_assessments', 'scf_financing_orders',
    'scf_insurance_policies', 'scf_receivables', 'system_configs', 'traceability_chain_nodes', 'traceability_configs',
    'traceability_nodes', 'traceability_record_entries', 'traceability_records', 'transports', 'uploaded_files',
    'user_groups', 'users', 'vehicles', 'warehouses'
    ])
)
SELECT r.rolname,
       count(*) FILTER (WHERE has_table_privilege(r.rolname, t.oid, 'SELECT')) AS can_select,
       count(*) FILTER (WHERE has_table_privilege(r.rolname, t.oid, 'INSERT,UPDATE,DELETE,TRUNCATE')) AS can_write,
       count(*) FILTER (WHERE has_table_privilege(r.rolname, t.oid, 'REFERENCES,TRIGGER')) AS can_ref_trigger,
       count(*) FILTER (WHERE has_any_column_privilege(r.rolname, t.oid, 'SELECT,INSERT,UPDATE,REFERENCES')) AS any_column,
       count(*) AS target_tables
FROM targets t CROSS JOIN (VALUES ('anon'), ('authenticated')) r(rolname)
GROUP BY r.rolname ORDER BY 1;

-- [2] funeng 目标表拥有的序列：有效权限。执行后应全部为 0
SELECT r.rolname,
       count(*) FILTER (WHERE has_sequence_privilege(r.rolname, s.oid, 'USAGE,SELECT,UPDATE')) AS any_privilege,
       count(*) AS target_sequences
FROM pg_depend d
JOIN pg_class s ON s.oid = d.objid AND s.relkind = 'S'
JOIN pg_class t ON t.oid = d.refobjid
CROSS JOIN (VALUES ('anon'), ('authenticated')) r(rolname)
WHERE d.classid = 'pg_class'::regclass AND d.refclassid = 'pg_class'::regclass AND d.deptype IN ('a','i')
  AND t.relnamespace = 'public'::regnamespace
  AND t.relname = ANY (ARRAY[
    'agri_collection_runs',
    'activities', 'admin_operation_logs', 'admin_roles', 'admin_users', 'adoption_categories',
    'adoption_configs', 'adoption_orders', 'agri_data_import_runs', 'agri_data_sources', 'campaigns',
    'cargo_owners', 'categories', 'cold_chain_inbound_appointments', 'cold_chain_inbound_order_items', 'cold_chain_inbound_orders',
    'cold_chain_inventory_alerts', 'cold_chain_inventory_rules', 'cold_chain_operating_costs', 'cold_chain_operation_batches', 'cold_chain_operation_tasks',
    'cold_chain_operators', 'cold_chain_quality_inspections', 'cold_chain_reference_nodes', 'cold_chain_sensors', 'cold_chain_temperature_alerts',
    'cold_chain_temperature_readings', 'cold_chain_warehouses', 'cold_chain_zones', 'coupons', 'crop_growth_models',
    'crops', 'decision_records', 'device_logs', 'device_types', 'devices',
    'environment_readings', 'export_tasks', 'farm_info', 'funeng_migration_conflicts', 'industry_observations',
    'iot_devices', 'irrigation_records', 'irrigation_zones', 'land_parcels', 'lands',
    'market_price_observations', 'marketing_orders', 'marketing_traffic_daily', 'members', 'monitoring_points',
    'monitoring_records', 'products', 'rental_orders', 'scf_credit_assessments', 'scf_financing_orders',
    'scf_insurance_policies', 'scf_receivables', 'system_configs', 'traceability_chain_nodes', 'traceability_configs',
    'traceability_nodes', 'traceability_record_entries', 'traceability_records', 'transports', 'uploaded_files',
    'user_groups', 'users', 'vehicles', 'warehouses'
  ])
GROUP BY r.rolname ORDER BY 1;

-- [3] 非 funeng 对象（如 todos）：迁移不改动，执行前后应完全一致
SELECT c.relname, c.relkind, pg_get_userbyid(c.relowner) AS owner, c.relacl::text AS acl, c.relrowsecurity AS rls
FROM pg_class c
WHERE c.relnamespace = 'public'::regnamespace AND c.relkind IN ('r','p','v','m','f')
  AND NOT (c.relname = ANY (ARRAY[
    'agri_collection_runs',
    'activities', 'admin_operation_logs', 'admin_roles', 'admin_users', 'adoption_categories',
    'adoption_configs', 'adoption_orders', 'agri_data_import_runs', 'agri_data_sources', 'campaigns',
    'cargo_owners', 'categories', 'cold_chain_inbound_appointments', 'cold_chain_inbound_order_items', 'cold_chain_inbound_orders',
    'cold_chain_inventory_alerts', 'cold_chain_inventory_rules', 'cold_chain_operating_costs', 'cold_chain_operation_batches', 'cold_chain_operation_tasks',
    'cold_chain_operators', 'cold_chain_quality_inspections', 'cold_chain_reference_nodes', 'cold_chain_sensors', 'cold_chain_temperature_alerts',
    'cold_chain_temperature_readings', 'cold_chain_warehouses', 'cold_chain_zones', 'coupons', 'crop_growth_models',
    'crops', 'decision_records', 'device_logs', 'device_types', 'devices',
    'environment_readings', 'export_tasks', 'farm_info', 'funeng_migration_conflicts', 'industry_observations',
    'iot_devices', 'irrigation_records', 'irrigation_zones', 'land_parcels', 'lands',
    'market_price_observations', 'marketing_orders', 'marketing_traffic_daily', 'members', 'monitoring_points',
    'monitoring_records', 'products', 'rental_orders', 'scf_credit_assessments', 'scf_financing_orders',
    'scf_insurance_policies', 'scf_receivables', 'system_configs', 'traceability_chain_nodes', 'traceability_configs',
    'traceability_nodes', 'traceability_record_entries', 'traceability_records', 'transports', 'uploaded_files',
    'user_groups', 'users', 'vehicles', 'warehouses'
  ]))
ORDER BY 1;

-- [4] RLS 策略（收回表权限后，针对 anon/authenticated/PUBLIC 的策略在 funeng 表上即失效；非 funeng 表不受影响）
SELECT schemaname, tablename, policyname, cmd, roles, qual
FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename, policyname;

-- [5] 对象属主（目标须全部为 postgres，否则迁移报错回滚）
SELECT c.relkind, pg_get_userbyid(c.relowner) AS owner, count(*)
FROM pg_class c
WHERE c.relnamespace = 'public'::regnamespace AND c.relkind IN ('r','p','v','m','f','S')
GROUP BY 1, 2 ORDER BY 1, 2;

-- [6] public 的默认权限（所有角色）。执行后仅 postgres 的 r/S 行不应再含 anon/authenticated；
--     函数(f)等其他对象类型不在撤权范围，执行前后应保持不变。
--     supabase_admin 行本迁移不修改，其新建对象仍会默认授予 anon/authenticated
SELECT pg_get_userbyid(d.defaclrole) AS creator_role, d.defaclobjtype AS objtype, d.defaclacl::text AS acl
FROM pg_default_acl d
WHERE d.defaclnamespace = 'public'::regnamespace OR d.defaclnamespace = 0
ORDER BY 1, 2;
