# S16 · control_client（Qt）

> 状态：`[x] 已完成`（教学骨架）

## 1. 目标

简易地面站客户端：启动后 HTTP 拉 BFF dashboard 并展示文本。对照 `eo_pod_gcs` 的「控制端拉状态」思路。

## 2. 前置

- Qt5/Qt6 开发包（`qtbase5-dev` 等）  
- control_bff `:8105` 已起  

若本机未装 Qt，可只读源码理解流程，不强制编过。

## 3. 操作

源码：`platform/clients/control_client/src/main.cpp`

要点：

1. `QApplication` + 主窗口 `QLabel`  
2. `QNetworkAccessManager::get` → `http://127.0.0.1:8105/api/bff/dashboard`  
3. `finished` 槽把 JSON/文本设到 Label；失败提示先起 BFF  

编译（示例，视本机 Qt 而定）：

```bash
# 若仓库已有 CMake 目标则：
# cmake --build build --target control_client
# 或用 qmake 独立工程（教学可自行加）
```

## 4. 设计说明

- 客户端**不直连**五个微服务，只打 BFF（企业常见 BFF 模式）。  
- 生产应：登录拿 JWT、定时刷新、预览窗播 `/preview` 或 `/vod`。  
- 当前为最小骨架，便于对照 GCS 再扩展。

## 5. 验收

- [x] 源码完整可读；BFF 可用时能展示 dashboard 文本  
- [ ] （可选）本机装 Qt 并跑出窗口  
