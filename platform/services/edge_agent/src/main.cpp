/**
 * @file main.cpp
 * @brief edge_agent：插件采帧 + 环缓 + 心跳 + 会话目录落盘元数据
 * 对照 eo_pod_server：插件 ABI / CameraHub / 会话目录思想
 */
#include "emp/Logger.h"
#include "emp/PluginLoader.h"
#include "emp/RingBuffer.h"
#include "emp/Types.h"

#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <sys/stat.h>

namespace {

bool http_post_json(const std::string& url, const std::string& json) {
    const std::string cmd =
        "curl -sS -m 2 -X POST '" + url +
        "' -H 'Content-Type: application/json' -d '" + json + "' >/dev/null 2>&1";
    return std::system(cmd.c_str()) == 0;
}

/** @brief 递归创建目录（简化 mkdir -p） */
void mkdir_p(const std::string& path) {
    std::string cmd = "mkdir -p '" + path + "'";
    std::system(cmd.c_str());
}

}  // namespace

int main(int argc, char** argv) {
    emp::Logger log("edge_agent");
    const char* device_code = std::getenv("EMP_DEVICE_CODE");
    if (!device_code) device_code = "edge-sim-001";
    const char* device_url = std::getenv("EMP_DEVICE_URL");
    if (!device_url) device_url = "http://127.0.0.1:8101/api/devices/heartbeat";
    const char* session_url = std::getenv("EMP_SESSION_URL");
    if (!session_url) session_url = "http://127.0.0.1:8102/api/sessions";
    const char* data_root = std::getenv("EMP_DATA_ROOT");
    if (!data_root) data_root = "data/sessions";

    int max_frames = 30;
    if (const char* f = std::getenv("EMP_FRAMES")) max_frames = std::atoi(f);

    std::string plugin_path = "build/lib/libemp_cam_Virtual.so";
    if (argc >= 2) plugin_path = argv[1];

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

    // 会话：时间戳命名，创建目录并通知 session_service
    const std::string session_code = std::string("sess-edge-") + std::to_string(emp::now_ns());
    const std::string session_dir = std::string(data_root) + "/" + session_code + "/cam0";
    mkdir_p(session_dir);
    {
        std::ostringstream start_json;
        start_json << "{\"device_code\":\"" << device_code
                   << "\",\"session_code\":\"" << session_code
                   << "\",\"storage_root\":\"" << data_root << "/" << session_code << "\"}";
        if (http_post_json(std::string(session_url) + "/start", start_json.str())) {
            log.info("会话已开始: " + session_code);
        } else {
            log.warn("session start 失败（服务可能未启动，仍继续本地落盘）");
        }
    }

    emp::RingBuffer<EmpFrameMeta> ring(8);
    std::ofstream index_file(session_dir + "/frames.index");  // 帧索引：每行 frame_id,ts_ns,w,h
    for (int i = 0; i < max_frames; ++i) {
        EmpFrameMeta meta{};
        if (loader.grab(cam, &meta) != 0) {
            log.warn("grab 失败");
            continue;
        }
        ring.push_overwrite(meta);
        if (index_file) {
            index_file << meta.frame_id << "," << meta.ts_ns << "," << meta.width << ","
                       << meta.height << "\n";
        }
        // 占位「帧文件」（真实 JPEG 后续接编码器）；便于 indexer 登记路径
        {
            std::ostringstream name;
            name << session_dir << "/" << meta.frame_id << ".meta";
            std::ofstream ofs(name.str());
            ofs << "frame_id=" << meta.frame_id << "\n";
        }
        if (i % 5 == 0) {
            std::ostringstream oss;
            oss << "{\"device_code\":\"" << device_code
                << "\",\"status\":\"online\",\"platform\":\"wsl\"}";
            if (http_post_json(device_url, oss.str())) {
                log.info("心跳已发送");
            } else {
                log.warn("心跳发送失败");
            }
        }
        log.info("frame_id=" + std::to_string(meta.frame_id) +
                 " ring=" + std::to_string(ring.size()));
    }
    index_file.close();

    {
        std::ostringstream end_json;
        end_json << "{\"device_code\":\"" << device_code
                 << "\",\"session_code\":\"" << session_code << "\",\"status\":\"closed\"}";
        http_post_json(std::string(session_url) + "/end", end_json.str());
    }

    // 通知 indexer 登记索引文件
    {
        std::ostringstream asset;
        asset << "{\"session_code\":\"" << session_code
              << "\",\"asset_type\":\"frame_index\",\"relative_path\":\"cam0/frames.index\",\"byte_size\":0}";
        http_post_json("http://127.0.0.1:8103/api/assets", asset.str());
    }

    loader.destroy(cam);
    log.info("edge_agent 正常退出 session=" + session_code);
    return 0;
}
