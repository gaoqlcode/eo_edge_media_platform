/**
 * @file VirtualCamera.cpp
 * @brief Virtual 相机插件：按帧率 sleep 并返回元数据
 * 对照 eo_pod_server plugins/camera/Virtual
 */
#include "emp/CameraPluginAbi.h"
#include "emp/Types.h"

#include <chrono>
#include <cstring>
#include <thread>

struct EmpCamera {
    unsigned long long next_id = 0;  // 下一帧号
    int width = 1280;                // 宽
    int height = 720;                // 高
    int fps = 10;                    // 帧率
};

extern "C" {

EmpCamera* emp_create_camera(void) { return new EmpCamera(); }

void emp_destroy_camera(EmpCamera* cam) { delete cam; }

const char* emp_camera_plugin_id(void) { return "Virtual"; }

int emp_camera_grab(EmpCamera* cam, EmpFrameMeta* out) {
    if (!cam || !out) {
        return -1;
    }
    const int period_ms = 1000 / (cam->fps > 0 ? cam->fps : 1);
    std::this_thread::sleep_for(std::chrono::milliseconds(period_ms));
    out->frame_id = cam->next_id++;
    out->ts_ns = emp::now_ns();
    out->width = cam->width;
    out->height = cam->height;
    return 0;
}

}  // extern "C"
