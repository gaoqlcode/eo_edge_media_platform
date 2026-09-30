# S12 · alarm_service

> 状态：`[x] 已完成`

## 1. 目标

告警创建、列表、确认（ack）；写操作需角色并审计。

端口：**8104**。

## 2. 前置

S04；可选关联 `device_code`。

## 3. 操作

```bash
# API Key
curl -s -X POST http://127.0.0.1:8104/api/alarms \
  -H 'X-API-Key: emp-dev-key' -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","severity":"warning","code":"TEMP_HIGH","message":"演示告警"}'

# JWT（operator/admin）
TOK=$(curl -s -X POST http://127.0.0.1:8105/api/bff/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -X POST http://127.0.0.1:8104/api/alarms \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -d '{"severity":"info","code":"JWT_ALARM","message":"jwt ok"}'

curl -s http://127.0.0.1:8104/api/alarms | head -c 400; echo
# ack
# curl -s -X POST http://127.0.0.1:8104/api/alarms/<id>/ack -H 'X-API-Key: emp-dev-key'
```

RBAC：`admin|service|operator`。设备 role **不能**造告警（除非另行放开）。

## 4. 设计说明

- severity：info/warning/critical（字符串约定）。  
- 列表按 `occurred_at` 倒序限制 100 条。  
- 审计命令：`alarm.create` / `alarm.ack`。

## 5. 验收

- [x] 双模创建；列表；审计有行；E2E 含 JWT 告警  
