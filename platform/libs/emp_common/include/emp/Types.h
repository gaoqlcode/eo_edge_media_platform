/**
 * @file Types.h
 * @brief EMP C++ 公共基础类型
 * 内容：设备编号别名、纳秒时间戳、心跳结构
 */
#pragma once
#include <chrono>
#include <cstdint>
#include <string>

namespace emp {

using DeviceCode = std::string;  // 设备业务编号
using TimestampNs = std::uint64_t;  // 纳秒时间戳

/** @brief 返回当前墙钟纳秒时间戳 */
inline TimestampNs now_ns() {
    using clock = std::chrono::system_clock;
    return static_cast<TimestampNs>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(
            clock::now().time_since_epoch())
            .count());
}

/** @brief 心跳载荷（边端上报） */
struct Heartbeat {
    DeviceCode device_code;  // 设备号
    std::string platform;    // wsl/rk3588
    std::string status;      // online/offline/fault
    TimestampNs ts_ns;       // 时间戳
};

}  // namespace emp
