# AGENTS.md — 多智能体 / 协作者必读

## 仓库是什么

`eo_edge_media_platform`：企业级边缘媒体学习与实战平台（嵌入式边端 + 音视频 + 微服务）。  
**复刻入口**：[`docs/rebuild/00_复刻总索引.md`](docs/rebuild/00_复刻总索引.md)

## 参考工程（只读，不拷进本仓）

- 吊舱边端：`/home/gaoql/eo_pod_server`
- 地面站客户端：`/home/gaoql/eo_pod_gcs`

禁止整文件粘贴；对照行为与模块边界后自研。

## GitHub 远端

- `git@github.com:gaoqlcode/eo_edge_media_platform.git`
- 推送前需本机 SSH 公钥已添加到 GitHub（见 `docs/ops/ssh_setup.md`）

## 分支约定

| 分支 | 用途 |
|------|------|
| `main` | 稳定线 |
| `phase/N-*` | 阶段集成 |
| `feat/<模块>-*` | 单模块/插件 |
| `docs/*` | 文档 |
| `fix/*` | 修复 |

## 模块所有权（并行时少抢同一目录）

- `docs/rebuild/**`、`docs/learning/**`：文档
- `platform/infra/**`：基础设施
- `platform/libs/**`：公共库（先合再消费）
- `platform/services/<name>/**`：一服务一 Agent
- `platform/services/edge_agent/plugins/<name>/**`：一插件一 Agent
- `platform/clients/control_client/**`：Qt 客户端
- `labs/**`：练习
- `platform/protocols/**`：协议先行

## 硬性规则

1. **文档与代码同提交**：改功能必须更新对应 `docs/rebuild/Sxx_*.md` 状态标记  
2. 状态标记：`[ ] 计划中` / `[~] 进行中` / `[x] 已完成` / `[!]` 有差异说明  
3. 提交信息：`类型(范围): 中文简述`  
4. 插件化：边端主机不绑死具体相机；新设备走 `plugins/` + C ABI  
5. 不提交 `.env`、私钥、`build/`、编译出的 `.so`

## 注释标准（自研代码）

文件头说明 + 函数总结注释 + 关键逻辑行中文注释。
