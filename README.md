# EO Edge Media Platform

企业级边缘媒体平台（学习 + 实战）：插件化边端、媒体网关、Python 微服务、PostgreSQL / Redis / RabbitMQ。

## 现在是什么水平？

**可联调企业骨架 + 学习文档详解 + RBAC/审计起步**，尚非完整生产产品。  
详见：[企业级成熟度](docs/architecture/企业级成熟度.md) · [学习路线图](docs/architecture/企业级与学习路线图.md)

已有：微服务、PG/Redis/MQ、插件边端、JPEG 预览、自动 H.264、`/vod`、JWT/API Key/设备 Token、RBAC、审计、traceparent/span、运维手册、详解学习章。  
仍缺：OTEL Exporter、真流媒体、板端硬编。

## 快速验收

```bash
bash scripts/start_infra_local.sh
bash scripts/e2e_test.sh
```

成功应看到：`E2E PASSED (enterprise checks)`

## 文档

1. 复刻顺序：[`docs/rebuild/00_复刻总索引.md`](docs/rebuild/00_复刻总索引.md)
2. 学习入口：[`docs/learning/00_入学与复刻入口.md`](docs/learning/00_入学与复刻入口.md)
3. 路线图：[`docs/architecture/企业级与学习路线图.md`](docs/architecture/企业级与学习路线图.md)
4. 运维：[`docs/ops/运维手册.md`](docs/ops/运维手册.md)
5. 多智能体：[`AGENTS.md`](AGENTS.md)

## 参考工程（只读）

- `/home/gaoql/eo_pod_server`
- `/home/gaoql/eo_pod_gcs`

## 远端

https://github.com/gaoqlcode/eo_edge_media_platform
