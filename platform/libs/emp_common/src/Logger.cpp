/**
 * @file Logger.cpp
 * @brief Logger 实现：时间 | 级别 | 模块 | 消息
 */
#include "emp/Logger.h"
#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>

namespace emp {

Logger::Logger(std::string module_name) : module_name_(std::move(module_name)) {}

void Logger::info(const std::string& message) const { write("INFO", message); }
void Logger::warn(const std::string& message) const { write("WARN", message); }
void Logger::error(const std::string& message) const { write("ERROR", message); }

void Logger::write(const char* level, const std::string& message) const {
    using clock = std::chrono::system_clock;
    const auto now = clock::now();
    const std::time_t t = clock::to_time_t(now);
    std::tm tm_buf{};
    localtime_r(&t, &tm_buf);
    std::ostringstream oss;
    oss << std::put_time(&tm_buf, "%F %T") << " | " << level << " | "
        << module_name_ << " | " << message;
    std::cerr << oss.str() << std::endl;
}

}  // namespace emp
