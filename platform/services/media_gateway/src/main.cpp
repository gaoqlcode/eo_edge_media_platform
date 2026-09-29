/**
 * @file main.cpp
 * @brief media_gateway：简易 TCP 健康口 + 内存会话表
 * 预览协议后续扩展；对照 PreviewServer/GcsBridge 演进为网关
 */
#include "emp/Logger.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>
#include <map>
#include <mutex>
#include <string>

namespace {
std::mutex g_mu;  // 保护会话表
std::map<std::string, std::string> g_sessions;  // session_id -> device_code
}  // namespace

/** @brief 处理一行文本命令：PING / REGISTER id device / LIST */
std::string handle_line(const std::string& line) {
    if (line == "PING") {
        return "PONG\n";
    }
    if (line.rfind("REGISTER ", 0) == 0) {
        // REGISTER <session> <device>
        const auto rest = line.substr(9);
        const auto sp = rest.find(' ');
        if (sp == std::string::npos) {
            return "ERR bad register\n";
        }
        const auto sid = rest.substr(0, sp);
        const auto dev = rest.substr(sp + 1);
        {
            std::lock_guard<std::mutex> lock(g_mu);
            g_sessions[sid] = dev;
        }
        return "OK registered\n";
    }
    if (line == "LIST") {
        std::lock_guard<std::mutex> lock(g_mu);
        std::string out = "OK count=" + std::to_string(g_sessions.size()) + "\n";
        for (const auto& kv : g_sessions) {
            out += kv.first + "->" + kv.second + "\n";
        }
        return out;
    }
    return "ERR unknown\n";
}

int main() {
    emp::Logger log("media_gateway");
    const int port = 9100;
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        log.error("socket 失败");
        return 1;
    }
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    if (bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        log.error("bind 失败");
        close(fd);
        return 1;
    }
    listen(fd, 8);
    log.info("media_gateway 监听 0.0.0.0:" + std::to_string(port));

    // 单连接循环（教学简化；企业版用多线程/epoll）
    while (true) {
        int cfd = accept(fd, nullptr, nullptr);
        if (cfd < 0) {
            continue;
        }
        char buf[512];
        const ssize_t n = read(cfd, buf, sizeof(buf) - 1);
        if (n > 0) {
            buf[n] = '\0';
            std::string line(buf);
            while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) {
                line.pop_back();
            }
            const std::string resp = handle_line(line);
            write(cfd, resp.data(), resp.size());
        }
        close(cfd);
    }
    return 0;
}
