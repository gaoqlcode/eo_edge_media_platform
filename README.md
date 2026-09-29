# EO Edge Media Platform

企业级边缘媒体平台（学习 + 实战）：插件化边端、媒体网关、Python 微服务、PostgreSQL / Redis / RabbitMQ。

## 你应该先读哪里

1. **从头复刻整个项目**：[`docs/rebuild/00_复刻总索引.md`](docs/rebuild/00_复刻总索引.md)（按 S00→S18 顺序）  
2. **多智能体约定**：[`AGENTS.md`](AGENTS.md)  
3. **SSH / Git**：[`docs/ops/ssh_setup.md`](docs/ops/ssh_setup.md)、[`docs/ops/git_workflow.md`](docs/ops/git_workflow.md)  
4. **概念学习**：[`docs/learning/`](docs/learning/)  

## 参考工程（本机路径，不在本仓库内）

| 角色 | 路径 |
|------|------|
| 吊舱边端参考 | `/home/gaoql/eo_pod_server` |
| 地面站参考 | `/home/gaoql/eo_pod_gcs` |

## 远端

```text
git@github.com:gaoqlcode/eo_edge_media_platform.git
```

## 当前阶段

**Phase 0**：仓库骨架 + 复刻索引 + Git/SSH 约定。业务代码按 Sxx 逐步实现。

## 目录速览

```text
docs/rebuild/     复刻步骤（开发顺序）
docs/learning/    学习课程
platform/         平台代码（服务/库/协议/客户端）
labs/             语法/数据结构/算法练习
scripts/          脚本
```
