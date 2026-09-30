# S15 · media_gateway

> 状态：`[x] 已完成`

## 1. 目标

TCP 会话登记 + HTTP JPEG 预览拉取（对照地面站 PreviewServer）。

## 2. 前置

edge_agent 已写出 `data/preview/<device>/latest.jpg`（或设 `EMP_PREVIEW_ROOT`）。

## 3. 操作

```bash
./build/bin/media_gateway
# TCP
echo PING | nc 127.0.0.1 9100
# HTTP
curl -o /tmp/p.jpg "http://127.0.0.1:9101/preview?device=edge-e2e-pg"
```

端口：TCP `9100`，HTTP `9101`。

## 4. 关键设计

边端写盘、网关读盘；教学版每连接一线程。生产用线程池/零拷贝与鉴权。

## 5. 验收

- [x] TCP `PING` → `PONG`
- [x] 存在 latest.jpg 时 `/preview` 返回 `image/jpeg`
