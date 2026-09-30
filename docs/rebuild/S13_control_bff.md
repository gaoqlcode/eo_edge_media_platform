# S13 · control_bff

> 状态：`[x] 已完成`

## 1. 目标

- 聚合设备/会话/告警只读视图，减少客户端扇出  
- 教学用账号密码登录，签发 JWT  

端口：**8105**。学习对照：[60_微服务](../learning/60_微服务.md)、[15_Python](../learning/15_Python语法与FastAPI.md)

## 2. 前置

S08～S12 可起；下游 `EMP_API_KEY` 一致。

## 3. 操作

```bash
# 登录
curl -s -X POST http://127.0.0.1:8105/api/bff/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}'
# 期望含 access_token / token_type / expires_in

# 身份
curl -s http://127.0.0.1:8105/api/bff/me \
  -H "Authorization: Bearer <token>"

# 仪表盘（下游：devices 无 Key；sessions 带 Key；alarms 无 Key）
curl -s http://127.0.0.1:8105/api/bff/dashboard | head -c 500; echo
```

环境变量：

| 变量 | 默认 | 含义 |
|------|------|------|
| EMP_ADMIN_USER | admin | 登录名 |
| EMP_ADMIN_PASS | admin123 | 密码 |
| EMP_JWT_SECRET | emp-jwt-dev-secret-change-me | HS256 密钥 |
| EMP_JWT_TTL | 3600 | 秒 |
| EMP_API_KEY | emp-dev-key | 调下游 |

代码：`platform/services/control_bff/app.py`；签发：`emp_py/jwt_auth.py`。

## 4. 设计说明

- BFF **对外** JWT，**对内**服务 Key，职责分离。  
- dashboard 部分失败写入 `errors[]`，不整页 500（教学友好）。  
- 生产：OIDC/LDAP、短 TTL + refresh、密钥轮换；禁止默认密码。

## 5. 验收

- [x] login / me / dashboard  
- [x] JWT 可调 alarm 写接口（E2E）  
