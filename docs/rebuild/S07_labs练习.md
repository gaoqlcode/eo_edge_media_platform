# S07 · labs 练习

> 状态：`[x] 已完成`

## 1. 目标

用最小可执行程序练 C++ 公共库，不依赖整套微服务。

## 2. 前置

S05；CMake 可编译。

## 3. 操作

| Lab | 源码 | 目标 | 练什么 |
|-----|------|------|--------|
| lab_syntax | `labs/cpp_syntax/hello_types.cpp` | Types + Logger | 基本类型与日志 |
| lab_ringbuffer | `labs/data_structures/ringbuffer_demo.cpp` | RingBuffer | 有界缓冲 |

```bash
cmake -S . -B build && cmake --build build --target lab_syntax lab_ringbuffer -j$(nproc)
./build/bin/lab_syntax
./build/bin/lab_ringbuffer
ctest --test-dir build --output-on-failure
```

## 4. 设计说明

labs 链接 `emp_common`，与 edge_agent 同一套库；改 RingBuffer 后 labs 立刻反映。

建议作业：把 capacity 改成 2，连续 push 5 次，手算剩余元素再跑验证。

## 5. 验收

- [x] 两 lab 退出码 0；ctest 绿  
