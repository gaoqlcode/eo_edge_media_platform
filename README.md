# EO Edge Media Platform

企业级边缘媒体平台（学习 + 实战）：插件化边端、媒体网关、Python 微服务、PostgreSQL / Redis / RabbitMQ。

## 现在是什么水平？

**可联调的企业骨架 + 已开始加固**，还不是可直接上生产的完整产品。  
详见：[docs/architecture/企业级成熟度.md](docs/architecture/企业级成熟度.md)

已有：微服务拆分、PG、Redis/MQ、插件边端、API Key、结构化日志、`/metrics`、Traefik/Prometheus、CI、E2E。  
仍缺：真视频编码预览、JWT/RBAC、全链路 tracing、板端硬编与完整运维。

## 快速验收

```bash
bash scripts/start_infra_local.sh
bash scripts/e2e_test.sh
```

成功应看到：`E2E PASSED (enterprise checks)`

## 文档

1. 复刻顺序：[`docs/rebuild/00_复刻总索引.md`](docs/rebuild/00_复刻总索引.md)
2. 多智能体：[`AGENTS.md`](AGENTS.md)
3. 学习：[`docs/learning/`](docs/learning/)

## 参考工程（只读）

- `/home/gaoql/eo_pod_server`
- `/home/gaoql/eo_pod_gcs`

## 远端

https://github.com/gaoqlcode/eo_edge_media_platform
