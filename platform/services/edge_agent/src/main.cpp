/**
 * @file main.cpp
 * @brief edge_agent：插件采帧 → JPEG 落盘 → 预览 latest.jpg → 心跳/会话 API
 */
#include "emp/JpegWriter.h"
#include "emp/Logger.h"
#include "emp/PluginLoader.h"
#include "emp/RingBuffer.h"
#include "emp/Types.h"

#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>

namespace {

bool http_post_json(const std::string& url, const std::string& json) {
    const std::string cmd =
        "curl -sS -m 2 -X POST '" + url +
        "' -H 'Content-Type: application/json' -d '" + json + "' >/dev/null 2>&1";
    return std::system(cmd.c_str()) == 0;
}

void mkdir_p(const std::string& path) {
    std::system(("mkdir -p '" + path + "'").c_str());
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
    const char* preview_root = std::getenv("EMP_PREVIEW_ROOT");
    if (!preview_root) preview_root = "data/preview";

    int max_frames = 30;
    if (const char* f = std::getenv("EMP_FRAMES")) max_frames = std::atoi(f);
    // 预览分辨率（低于采集元数据也可，教学用固定）
    const int pw = 320;
    const int ph = 180;

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

    const std::string session_code = std::string("sess-edge-") + std::to_string(emp::now_ns());
    const std::string session_dir = std::string(data_root) + "/" + session_code + "/cam0";
    const std::string preview_dir = std::string(preview_root) + "/" + device_code;
    mkdir_p(session_dir);
    mkdir_p(preview_dir);

    {
        std::ostringstream start_json;
        start_json << "{\"device_code\":\"" << device_code
                   << "\",\"session_code\":\"" << session_code
                   << "\",\"storage_root\":\"" << data_root << "/" << session_code << "\"}";
        http_post_json(std::string(session_url) + "/start", start_json.str());
        log.info("会话已开始: " + session_code);
    }

    emp::RingBuffer<EmpFrameMeta> ring(8);
    std::ofstream index_file(session_dir + "/frames.index");
    for (int i = 0; i < max_frames; ++i) {
        EmpFrameMeta meta{};
        if (loader.grab(cam, &meta) != 0) {
            log.warn("grab 失败");
            continue;
        }
        ring.push_overwrite(meta);

        // 生成 JPEG：会话目录一帧一份 + 覆盖 latest 供网关预览
        auto rgb = emp::make_test_pattern_rgb(pw, ph, meta.frame_id);
        const std::string frame_jpg = session_dir + "/" + std::to_string(meta.frame_id) + ".jpg";
        const std::string latest_jpg = preview_dir + "/latest.jpg";
        if (emp::write_jpeg_file(frame_jpg, pw, ph, rgb, 80)) {
            emp::write_jpeg_file(latest_jpg, pw, ph, rgb, 80);
        } else {
            log.warn("写 JPEG 失败");
        }

        if (index_file) {
            index_file << meta.frame_id << "," << meta.ts_ns << "," << pw << "," << ph << "," << frame_jpg
                       << "\n";
        }

        if (i % 5 == 0) {
            std::ostringstream oss;
            oss << "{\"device_code\":\"" << device_code
                << "\",\"status\":\"online\",\"platform\":\"wsl\"}";
            http_post_json(device_url, oss.str());
            log.info("心跳已发送");
        }
        log.info("frame_id=" + std::to_string(meta.frame_id) + " jpeg=" + frame_jpg);
    }
    index_file.close();

    {
        std::ostringstream end_json;
        end_json << "{\"device_code\":\"" << device_code
                 << "\",\"session_code\":\"" << session_code << "\",\"status\":\"closed\"}";
        http_post_json(std::string(session_url) + "/end", end_json.str());
    }
    {
        std::ostringstream asset;
        asset << "{\"session_code\":\"" << session_code
              << "\",\"asset_type\":\"jpeg_seq\",\"relative_path\":\"cam0/\",\"byte_size\":0}";
        http_post_json("http://127.0.0.1:8103/api/assets", asset.str());
    }

    loader.destroy(cam);
    log.info("edge_agent 正常退出 session=" + session_code);
    return 0;
}
