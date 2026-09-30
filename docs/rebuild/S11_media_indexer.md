# S11 · media_indexer

> 状态：`[x] 已完成`

## 1. 目标

登记会话下媒体资产，提供回放索引 API。

端口：**8103**。

## 2. 前置

S10 会话已创建。

## 3. 操作

```bash
curl -s -X POST http://127.0.0.1:8103/api/assets \
  -H 'X-API-Key: emp-dev-key' -H 'Content-Type: application/json' \
  -d '{"session_code":"sess-demo-1","asset_type":"jpeg_seq","relative_path":"cam0/","byte_size":0}'

curl -s "http://127.0.0.1:8103/api/assets?session_code=sess-demo-1"
curl -s "http://127.0.0.1:8103/api/playback/sess-demo-1"
```

edge_agent 会登记：

- `jpeg_seq` → `cam0/`  
- `h264_mp4` → `cam0/preview.mp4`（编码成功时）

代码：`platform/services/media_indexer/app.py`

## 4. 设计说明

- indexer **只存元数据**，不存文件本体；文件在边端/共享盘。  
- `playback` 返回 `storage_root` + assets，客户端拼路径或走 gateway `/vod`。  
- `asset_type` 约定：`jpeg_seq` / `h264_mp4`（可扩展）。

## 5. 验收

- [x] add/list/playback；E2E 可见 h264_mp4  
