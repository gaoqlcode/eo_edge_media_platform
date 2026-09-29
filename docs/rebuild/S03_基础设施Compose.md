# S03 · 基础设施 Compose

> 状态：`[x] 已完成`

## 目标
提供 PostgreSQL / Redis / RabbitMQ / Traefik / Prometheus / Grafana 的 Compose 定义。

## 操作
```bash
docker compose -f platform/infra/docker-compose.yml up -d
```
无 Docker 时：跳过，E2E 用 SQLite（见总索引 `[!]`）。

## 验收
- [x] `platform/infra/docker-compose.yml` 存在
- [x] Traefik/Prometheus 配置文件存在
