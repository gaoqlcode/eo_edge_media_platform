# S08 · device_service

> 状态：`[x] 已完成`

## 1. 目标

设备注册、列表、心跳；写注册需 RBAC；心跳写 PG + Redis + MQ。

端口：**8101**。学习对照：[60_微服务](../learning/60_微服务.md)

## 2. 前置

S04 表；S05 emp_py；infra 已起。

## 3. 操作

```bash
bash scripts/start_python_services.sh
curl -s http://127.0.0.1:8101/health

# 无密钥 → 401
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:8101/api/devices \
  -H 'Content-Type: application/json' -d '{"device_code":"x","name":"x"}'

# 注册（admin/service）
curl -s -X POST http://127.0.0.1:8101/api/devices \
  -H 'X-API-Key: emp-dev-key' -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-demo","name":"演示边端","platform":"wsl"}'

# 心跳（开放，便于边端）
curl -s -X POST http://127.0.0.1:8101/api/devices/heartbeat \
  -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-demo","status":"online","platform":"wsl"}'

curl -s http://127.0.0.1:8101/api/devices/edge-demo/online
curl -s http://127.0.0.1:8101/metrics | head
```

代码：`platform/services/device_service/app.py`

## 4. 设计说明

- 注册：`require_roles("admin","service")` + `write_audit`  
- 心跳：更新 `last_seen_at`、`cache_set(device:online:*)`、`publish_event(emp.device.heartbeat)`  
- 列表只读暂不鉴权（学习期）；生产可收紧  

## 5. 验收

- [x] 401 / 注册 / 心跳 / metrics / 审计行  
