# S14 · edge_agent

> 状态：`[x] 已完成`

## 目标

插件化边端：dlopen 相机 → 环缓 → JPEG 落盘/预览 → 心跳/会话 → 可选 H.264 成片登记。

## 操作

```bash
cmake -S . -B build && cmake --build build -j$(nproc)
EMP_FRAMES=5 EMP_ROOT=$PWD EMP_ENCODE_H264=1 \
  EMP_DATA_ROOT=$PWD/data/sessions EMP_PREVIEW_ROOT=$PWD/data/preview \
  ./build/bin/edge_agent ./build/lib/libemp_cam_Virtual.so
```

环境：`EMP_API_KEY` / `EMP_DEVICE_TOKEN`；`EMP_ENCODE_H264=0` 可关编码。

## 对照

`/home/gaoql/eo_pod_server` 的 CameraPluginAbi / CameraHub。

## 验收

- [x] 插件 id=Virtual；心跳可达  
- [x] `latest.jpg` + 会话 JPEG  
- [x] 有 ffmpeg 时产出 `cam0/preview.mp4` 并登记 `h264_mp4` 资产  
