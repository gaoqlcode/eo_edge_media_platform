# EO Edge Media Platform

企业级边缘媒体平台（学习 + 实战）：插件化边端、媒体网关、Python 微服务、PostgreSQL（Docker）/ SQLite（本地自测）。

## 快速验收

```bash
python3 -m pip install --user -r requirements.txt
bash scripts/e2e_test.sh
```

成功应看到：`E2E PASSED`

## 文档入口

1. **复刻（按开发顺序）**：[`docs/rebuild/00_复刻总索引.md`](docs/rebuild/00_复刻总索引.md)
2. **多智能体约定**：[`AGENTS.md`](AGENTS.md)
3. **学习课程**：[`docs/learning/`](docs/learning/)
4. **SSH/Git**：[`docs/ops/`](docs/ops/)

## 参考工程（只读）

- `/home/gaoql/eo_pod_server`
- `/home/gaoql/eo_pod_gcs`

## 远端

https://github.com/gaoqlcode/eo_edge_media_platform

## 常用命令

```bash
# Python 微服务
bash scripts/start_python_services.sh
bash scripts/stop_python_services.sh

# C++
cmake -S . -B build && cmake --build build -j$(nproc)

# Qt 客户端
cmake -S platform/clients/control_client -B build-client && cmake --build build-client -j$(nproc)

# Docker 基础设施（需本机 Docker）
docker compose -f platform/infra/docker-compose.yml up -d
```
