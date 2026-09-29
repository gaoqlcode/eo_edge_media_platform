-- =============================================================================
-- 002_seed_demo.sql — 演示种子数据
-- =============================================================================
INSERT INTO tenants (code, name)
SELECT 'default', '默认学习租户'
WHERE NOT EXISTS (SELECT 1 FROM tenants WHERE code = 'default');

INSERT INTO devices (tenant_id, device_code, name, device_type, platform, status)
SELECT t.id, 'edge-sim-001', 'WSL模拟边端-001', 'sim', 'wsl', 'offline'
FROM tenants t
WHERE t.code = 'default'
  AND NOT EXISTS (
      SELECT 1 FROM devices d WHERE d.device_code = 'edge-sim-001' AND d.tenant_id = t.id
  );

INSERT INTO channels (device_id, channel_code, name, media_kind, config_json)
SELECT d.id, 'cam0', '模拟相机0', 'video', '{"width":1280,"height":720,"fps":15}'::jsonb
FROM devices d
JOIN tenants t ON t.id = d.tenant_id
WHERE d.device_code = 'edge-sim-001' AND t.code = 'default'
  AND NOT EXISTS (
      SELECT 1 FROM channels c WHERE c.device_id = d.id AND c.channel_code = 'cam0'
  );
