# S03 · 基础设施 Compose / 本机中间件

> 状态：`[x] 已完成`

## 目标

PostgreSQL + Redis + RabbitMQ 可用；Compose 与本机双路径。

## 路径 A：micromamba 本机（E2E 默认）

```bash
bash scripts/start_infra_local.sh
# PG: 127.0.0.1:55432 用户 emp 库 emp_platform
# Redis: 127.0.0.1:56379
```

## 路径 B：Docker Compose（企业一键）

镜像已可拉取时：

```bash
sudo docker-compose -f platform/infra/docker-compose.yml up -d
# emp_postgres :5432（用户/库 emp / emp_platform，密码 emp_dev_pass）
# emp_redis :6379、emp_rabbitmq :5672/:15672
```

仅起 PG：

```bash
sudo docker-compose -f platform/infra/docker-compose.yml up -d postgres
```

Hub 超时可用 DaoCloud：

```bash
sudo docker pull docker.m.daocloud.io/library/postgres:16
sudo docker tag docker.m.daocloud.io/library/postgres:16 postgres:16
```

> 注意：Compose PG `:5432` 与本机 micromamba `:55432` 并存，切库改 `DATABASE_URL`。

## 验收

- [x] `start_infra_local.sh` 可起 PG/Redis
- [x] Compose `emp_postgres` healthy，迁移表已建
- [x] `e2e_test.sh` 在 micromamba PG 下通过
