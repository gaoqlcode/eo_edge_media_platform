/**
 * @file PluginLoader.h
 * @brief dlopen 加载相机插件
 */
#pragma once
#include "emp/CameraPluginAbi.h"
#include <string>

namespace emp {

/** @brief 动态库插件加载器 */
class PluginLoader {
public:
    PluginLoader() = default;
    ~PluginLoader();  // 关闭 so

    PluginLoader(const PluginLoader&) = delete;
    PluginLoader& operator=(const PluginLoader&) = delete;

    /**
     * @brief 打开插件 so 并解析符号
     * @param path so 路径
     * @return true 成功
     */
    bool load(const std::string& path);

    EmpCamera* create() const;  // 调插件创建
    void destroy(EmpCamera* cam) const;  // 调插件销毁
    const char* plugin_id() const;  // 插件 id
    int grab(EmpCamera* cam, EmpFrameMeta* out) const;  // 抓帧

private:
    void* handle_ = nullptr;  // dlopen 句柄
    EmpCamera* (*create_fn_)(void) = nullptr;
    void (*destroy_fn_)(EmpCamera*) = nullptr;
    const char* (*id_fn_)(void) = nullptr;
    int (*grab_fn_)(EmpCamera*, EmpFrameMeta*) = nullptr;
};

}  // namespace emp
