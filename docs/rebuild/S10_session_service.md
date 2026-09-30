# S10 · session_service

> 状态：`[x] 已完成`

## 1. 目标

管理录制/采集会话的开始与结束；列表需鉴权；写操作审计。

端口：**8102**。

## 2. 前置

S08 设备已存在（会话外键依赖 `devices`）。

## 3. 操作

```bash
# 先确保设备存在（心跳可自动建）
curl -s -X POST http://127.0.0.1:8102/api/sessions/start \
  -H 'X-API-Key: emp-dev-key' -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","session_code":"sess-demo-1","storage_root":"data/sess-demo-1"}'

curl -s -X POST http://127.0.0.1:8102/api/sessions/end \
  -H 'X-API-Key: emp-dev-key' -H 'Content-Type: application/json' \
  -d '{"device_code":"edge-e2e-pg","session_code":"sess-demo-1","status":"closed"}'

curl -s http://127.0.0.1:8102/api/sessions -H 'X-API-Key: emp-dev-key'
```

边端用 `X-Device-Token` 亦可（`require_auth`）。  
代码：`platform/services/session_service/app.py`

## 4. 设计说明

- `session_code` 在设备维度唯一。  
- `storage_root` 指向落盘根；与 edge_agent `EMP_DATA_ROOT` 对齐便于对照。  
- start 写 `command_audits`（`session.start`）。

## 5. 验收

- [x] start/end/list；无 Key 列表 401；E2E 通过  
