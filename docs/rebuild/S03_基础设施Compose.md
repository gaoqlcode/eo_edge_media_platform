# S03 · 基础设施 Compose / 本机中间件

> 状态：`[x] 已完成`

## 目标
PostgreSQL + Redis 可用；Compose 文件齐全（Docker 镜像可拉取时一键起全栈）。

## 当前推荐路径（已验证）

无需 Docker 镜像时，用 micromamba 本机实例：

```bash
bash scripts/start_infra_local.sh
# PG: 127.0.0.1:55432 用户 emp 库 emp_platform
# Redis: 127.0.0.1:56379
```

## Docker 路径

```bash
# 需已安装 docker.io（sudo apt install docker.io docker-compose）
sudo docker-compose -f platform/infra/docker-compose.yml up -d
```

若 Docker Hub 超时，已配置 `/etc/docker/daemon.json` 镜像加速；仍失败时可：

```bash
sudo docker pull docker.m.daocloud.io/library/postgres:16
sudo docker tag docker.m.daocloud.io/library/postgres:16 postgres:16
```

## 验收

- [x] `start_infra_local.sh` 可起 PG/Redis
- [x] 迁移 SQL 已应用到 PG
- [x] `e2e_test.sh` 在 PostgreSQL 下通过（`psql` 可见设备行）
- [x] `docker-compose.yml` version 3.3 可用
