# S13 · control_bff

> 状态：`[x] 已完成`

## 1. 目标

聚合设备/会话/告警只读视图；提供教学用 JWT 登录。

## 2. 前置

S08–S12 服务可起；`EMP_API_KEY` 与下游一致。

## 3. 操作

```bash
# 登录
curl -s -X POST http://127.0.0.1:8105/api/bff/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 身份
curl -s http://127.0.0.1:8105/api/bff/me -H "Authorization: Bearer <token>"
# 仪表盘
curl -s http://127.0.0.1:8105/api/bff/dashboard
```

环境变量：`EMP_ADMIN_USER` / `EMP_ADMIN_PASS` / `EMP_JWT_SECRET` / `EMP_JWT_TTL`。

## 4. 关键设计

BFF 对下游带 `X-API-Key`；对外可发 JWT。生产应接 LDAP/OIDC，勿用固定账号。

## 5. 验收

- [x] `/api/bff/login` 返回 `access_token`
- [x] `/api/bff/me` 校验 Bearer
- [x] `/api/bff/dashboard` 聚合三源
