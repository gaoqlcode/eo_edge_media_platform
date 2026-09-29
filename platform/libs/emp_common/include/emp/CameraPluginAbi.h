/**
 * @file CameraPluginAbi.h
 * @brief 相机插件 C ABI（对照 eo_pod_server CameraPluginAbi）
 * 内容：插件 so 必须导出的三个符号；主机只依赖本头文件
 */
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/** 插件相机不透明句柄 */
typedef struct EmpCamera EmpCamera;

/** 一帧元数据（P0 不携带大像素缓冲，降低复杂度） */
typedef struct EmpFrameMeta {
    unsigned long long frame_id;  // 帧序号
    unsigned long long ts_ns;     // 时间戳纳秒
    int width;                    // 宽
    int height;                   // 高
} EmpFrameMeta;

/** 创建相机实例 */
EmpCamera* emp_create_camera(void);
/** 销毁相机实例 */
void emp_destroy_camera(EmpCamera* cam);
/** 插件标识字符串，如 Virtual */
const char* emp_camera_plugin_id(void);
/** 抓取下一帧元数据；成功返回 0 */
int emp_camera_grab(EmpCamera* cam, EmpFrameMeta* out);

#ifdef __cplusplus
}
#endif
