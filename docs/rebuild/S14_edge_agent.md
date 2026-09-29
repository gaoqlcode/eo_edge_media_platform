# S14 · edge_agent

> 状态：`[x] 已完成`

## 目标
插件化边端主机：dlopen Virtual 相机 → 环缓 → HTTP 心跳。

## 操作
```bash
cmake -S . -B build && cmake --build build -j$(nproc)
EMP_FRAMES=5 ./build/bin/edge_agent ./build/lib/libemp_cam_Virtual.so
```

## 对照
`/home/gaoql/eo_pod_server` 的 CameraPluginAbi / CameraHub。

## 验收
- [x] 插件 id=Virtual；可向 device_service 发心跳
