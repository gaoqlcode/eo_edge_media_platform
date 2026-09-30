# S09 · api_gateway（Traefik）

> 状态：`[x] 已完成`（Compose 路径）

## 1. 目标

用 Traefik 作可选统一入口，把多服务端口收敛为网关路由；本仓学习期也可直连 `:810x`。

## 2. 前置

Docker 可用；镜像 `traefik:v3.0`（见 Compose）。

## 3. 操作

```bash
sudo docker-compose -f platform/infra/docker-compose.yml up -d traefik
# 动态配置
cat platform/infra/traefik/dynamic.yml
# 仪表盘常映射 8088 → 8080
```

本机直连（无 Traefik 时）：

```text
8101 device · 8102 session · 8103 indexer · 8104 alarm · 8105 bff
```

应用侧 Compose 见 `platform/infra/docker-compose.app.yml`（可把服务打进容器，依赖 host PG）。

## 4. 设计说明

- 开发默认**直连端口**，降低心智负担。  
- 企业入口：TLS 终止、限流、统一鉴权头可在 Traefik/网关层加。  
- Prometheus 抓取各服务 `/metrics`：`platform/infra/prometheus/prometheus.yml`。

## 5. 验收

- [x] Compose 文件与 Traefik/Prometheus 配置齐全  
- [x] 无 Traefik 时 e2e 仍可通过直连完成  
