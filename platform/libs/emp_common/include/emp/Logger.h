/**
 * @file Logger.h
 * @brief 简易日志器
 */
#pragma once
#include <string>

namespace emp {

/** @brief 带模块前缀的日志 */
class Logger {
public:
    explicit Logger(std::string module_name);  // 保存模块名
    void info(const std::string& message) const;   // INFO
    void warn(const std::string& message) const;   // WARN
    void error(const std::string& message) const;  // ERROR
private:
    std::string module_name_;  // 模块前缀
    void write(const char* level, const std::string& message) const;  // 统一输出
};

}  // namespace emp
