/**
 * @file PluginLoader.cpp
 * @brief dlopen / dlsym 实现
 */
#include "emp/PluginLoader.h"
#include <dlfcn.h>

namespace emp {

PluginLoader::~PluginLoader() {
    if (handle_) {
        dlclose(handle_);
        handle_ = nullptr;
    }
}

bool PluginLoader::load(const std::string& path) {
    handle_ = dlopen(path.c_str(), RTLD_NOW);
    if (!handle_) {
        return false;
    }
    create_fn_ = reinterpret_cast<EmpCamera* (*)(void)>(dlsym(handle_, "emp_create_camera"));
    destroy_fn_ = reinterpret_cast<void (*)(EmpCamera*)>(dlsym(handle_, "emp_destroy_camera"));
    id_fn_ = reinterpret_cast<const char* (*)(void)>(dlsym(handle_, "emp_camera_plugin_id"));
    grab_fn_ = reinterpret_cast<int (*)(EmpCamera*, EmpFrameMeta*)>(dlsym(handle_, "emp_camera_grab"));
    return create_fn_ && destroy_fn_ && id_fn_ && grab_fn_;
}

EmpCamera* PluginLoader::create() const { return create_fn_ ? create_fn_() : nullptr; }
void PluginLoader::destroy(EmpCamera* cam) const {
    if (destroy_fn_ && cam) {
        destroy_fn_(cam);
    }
}
const char* PluginLoader::plugin_id() const { return id_fn_ ? id_fn_() : ""; }
int PluginLoader::grab(EmpCamera* cam, EmpFrameMeta* out) const {
    return grab_fn_ ? grab_fn_(cam, out) : -1;
}

}  // namespace emp
