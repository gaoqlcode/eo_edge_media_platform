/**
 * @file main.cpp
 * @brief edge_agent 主机：加载插件、采帧、HTTP 心跳到 device_service
 * 对照 eo_pod_server main + CameraHub 简化企业版
 */
#include "emp/Logger.h"
#include "emp/PluginLoader.h"
#include "emp/RingBuffer.h"
#include "emp/Types.h"

#include <atomic>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

namespace {

/** @brief 用系统 curl 发 JSON POST（避免引入第三方 HTTP 库） */
bool http_post_json(const std::string& url, const std::string& json) {
    const std::string cmd =
        "curl -sS -m 2 -X POST '" + url +
        "' -H 'Content-Type: application/json' -d '" + json + "' >/dev/null 2>&1";
    return std::system(cmd.c_str()) == 0;
}

}  // namespace

/**
 * @brief 程序入口
 * 参数：可选插件 so 路径；环境变量 EMP_DEVICE_CODE / EMP_DEVICE_URL / EMP_FRAMES
 */
int main(int argc, char** argv) {
    emp::Logger log("edge_agent");
    const char* device_code = std::getenv("EMP_DEVICE_CODE");
    if (!device_code) {
        device_code = "edge-sim-001";
    }
    const char* device_url = std::getenv("EMP_DEVICE_URL");
    if (!device_url) {
        device_url = "http://127.0.0.1:8101/api/devices/heartbeat";
    }
    int max_frames = 30;
    if (const char* f = std::getenv("EMP_FRAMES")) {
        max_frames = std::atoi(f);
    }

    std::string plugin_path = "build/lib/libemp_cam_Virtual.so";
    if (argc >= 2) {
        plugin_path = argv[1];
    }

    emp::PluginLoader loader;
    if (!loader.load(plugin_path)) {
        log.error(std::string("加载插件失败: ") + plugin_path);
        return 1;
    }
    log.info(std::string("插件已加载: ") + loader.plugin_id());

    EmpCamera* cam = loader.create();
    if (!cam) {
        log.error("创建相机失败");
        return 1;
    }

    emp::RingBuffer<EmpFrameMeta> ring(8);
    for (int i = 0; i < max_frames; ++i) {
        EmpFrameMeta meta{};
        if (loader.grab(cam, &meta) != 0) {
            log.warn("grab 失败");
            continue;
        }
        ring.push_overwrite(meta);
        if (i % 5 == 0) {
            std::ostringstream oss;
            oss << "{\"device_code\":\"" << device_code
                << "\",\"status\":\"online\",\"platform\":\"wsl\"}";
            if (http_post_json(device_url, oss.str())) {
                log.info("心跳已发送");
            } else {
                log.warn("心跳发送失败（device_service 可能未启动）");
            }
        }
        log.info("frame_id=" + std::to_string(meta.frame_id) +
                 " size=" + std::to_string(ring.size()));
    }

    loader.destroy(cam);
    log.info("edge_agent 正常退出");
    return 0;
}
