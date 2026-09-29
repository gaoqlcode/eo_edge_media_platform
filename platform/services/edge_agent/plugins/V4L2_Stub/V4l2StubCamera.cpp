/**
 * @file V4l2StubCamera.cpp
 * @brief V4L2 占位插件：当前环境无相机时行为与 Virtual 类似，plugin_id=V4L2_Stub
 * 上 RK3588 后替换为真实 V4L2 dequeue 实现
 */
#include "emp/CameraPluginAbi.h"
#include "emp/Types.h"
#include <chrono>
#include <thread>

struct EmpCamera {
    unsigned long long next_id = 0;
    int width = 1280;
    int height = 720;
    int fps = 10;
};

extern "C" {

EmpCamera* emp_create_camera(void) { return new EmpCamera(); }
void emp_destroy_camera(EmpCamera* cam) { delete cam; }
const char* emp_camera_plugin_id(void) { return "V4L2_Stub"; }

int emp_camera_grab(EmpCamera* cam, EmpFrameMeta* out) {
    if (!cam || !out) return -1;
    std::this_thread::sleep_for(std::chrono::milliseconds(1000 / (cam->fps > 0 ? cam->fps : 1)));
    out->frame_id = cam->next_id++;
    out->ts_ns = emp::now_ns();
    out->width = cam->width;
    out->height = cam->height;
    return 0;
}

}
