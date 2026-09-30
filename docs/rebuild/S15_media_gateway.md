# S15 · media_gateway

> 状态：`[x] 已完成`

## 1. 目标

TCP 会话登记 + HTTP JPEG 预览 + VOD 成片下载。

## 2. 前置

- 预览：`EMP_PREVIEW_ROOT/<device>/latest.jpg`  
- 成片：`EMP_SESSION_ROOT/<session>/cam0/preview.mp4`

## 3. 操作

```bash
EMP_PREVIEW_ROOT=$PWD/data/preview EMP_SESSION_ROOT=$PWD/data/sessions \
  ./build/bin/media_gateway
echo PING | nc 127.0.0.1 9100
curl -o /tmp/p.jpg "http://127.0.0.1:9101/preview?device=edge-e2e-pg"
curl -o /tmp/v.mp4 "http://127.0.0.1:9101/vod?session=sess-edge-...."
```

端口：TCP `9100`，HTTP `9101`。

## 4. 设计说明

边端写盘、网关读盘；`session` 参数禁止 `..` 与路径分隔。生产需鉴权与 Range。

## 5. 验收

- [x] TCP `PING` → `PONG`  
- [x] `/preview` → JPEG  
- [x] `/vod?session=` → MP4（成片存在时）  
