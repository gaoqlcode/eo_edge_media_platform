# 40 · PostgreSQL（对照本仓迁移与 ORM）

## 1. 学习目标

- 读懂 `001_init_schema.sql` 每张核心表的职责  
- 区分 **SQL 迁移** 与 **SQLAlchemy ORM**  
- 会用 `psql` 查设备/会话，并理解索引用途  

对应 S04、S08～S12。[05](./05_环境软件下载与工具链.md) 双路径端口。

---

## 2. 概念详解

### 2.1 为什么用 PostgreSQL

- 事务、约束、JSONB、扩展（`pgcrypto` 生成 UUID）  
- 企业控制面标准选择；本仓也可用 SQLite 降级联调  

### 2.2 核心表白话

| 表 | 存什么 |
|----|--------|
| `tenants` | 租户（多客户隔离的种子） |
| `devices` | 边端设备档案与在线状态 |
| `channels` | 设备上的通道（视频/其他） |
| `record_sessions` | 一次录制/采集会话 |
| `media_assets` | 会话下的文件资产（jpeg_seq、mp4…） |
| `alarm_events` | 告警 |
| `command_audits` | 命令/写操作审计（企业必备） |
| `outbox_events` | 可靠发消息的发件箱模式 |

### 2.3 约束与索引

- `UNIQUE (tenant_id, device_code)`：同租户设备编码不重复  
- `REFERENCES ... ON DELETE CASCADE`：删设备可级联通道等  
- `idx_devices_status`：按状态过滤  
- `idx_sessions_device_started`：某设备会话按时间倒序  

索引加快查询，但拖慢写入、占空间——只给高频条件建。

### 2.4 事务直觉

```sql
BEGIN;
-- 多条写
COMMIT;  -- 或 ROLLBACK
```

ORM 的 `db.commit()` 即提交当前事务。

### 2.5 迁移 vs ORM

| | 迁移 SQL | ORM models.py |
|--|----------|---------------|
| 权威 | **是**（生产以 SQL 为准） | 教学映射 |
| 用途 | 建表、改表版本化 | CRUD 方便 |
| 本仓 | `platform/infra/migrations/` | `emp_py/models.py` |

注意：PG 用 UUID 类型，ORM 教学版用 `String(36)` 存 UUID 字符串——属简化，读迁移时以 SQL 为准。

### 2.6 连接串

```text
postgresql+psycopg2://emp@127.0.0.1:55432/emp_platform          # Local
postgresql+psycopg2://emp:emp_dev_pass@127.0.0.1:5432/emp_platform  # Compose
```

驱动库：`psycopg2-binary`（见 05b）。

---

## 3. 下载与依赖

- Local：`bash scripts/start_infra_local.sh`  
- Compose：`postgres:16` 容器  
- 客户端：环境内 `psql` 或 `sudo apt install postgresql-client`

---

## 4. 本项目对照

- SQL：`platform/infra/migrations/001_init_schema.sql`、`002_seed_demo.sql`  
- ORM：`emp_py/models.py`  
- 使用示例：`device_service/app.py` 注册设备、心跳更新 `last_seen_at`

---

## 5. 动手实验

```bash
bash scripts/start_infra_local.sh
psql -h 127.0.0.1 -p 55432 -U emp -d emp_platform -c '\dt'
psql -h 127.0.0.1 -p 55432 -U emp -d emp_platform -c \
  "SELECT device_code,status,last_seen_at FROM devices ORDER BY updated_at DESC LIMIT 5;"
```

对照 `\d devices` 看列与索引。

---

## 6. 自测题

1. `media_assets.session_id` 外键指向哪张表？删会话会怎样（看 ON DELETE）？  
2. 为什么心跳既写 PG 又写 Redis？  
3. `command_audits` 空着不用，企业上线有什么风险？  

答案：1）`record_sessions`，级联删资产；2）权威落库 + 短 TTL 加速读；3）无法追责与审计。
