/**
 * @file main.cpp
 * @brief media_gateway：TCP 会话命令 + HTTP 预览 JPEG + VOD 成片
 *
 * HTTP:
 *   GET /health
 *   GET /preview?device=edge-sim-001   -> image/jpeg
 *   GET /vod?session=sess-edge-xxx     -> video/mp4 (cam0/preview.mp4)
 * TCP 文本:
 *   PING / REGISTER <sid> <device> / LIST
 */
#include "emp/Logger.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cstring>
#include <fstream>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {
std::mutex g_mu;
std::map<std::string, std::string> g_sessions;
std::string g_preview_root = "data/preview";
std::string g_session_root = "data/sessions";

std::string query_param(const std::string& path, const std::string& key, const std::string& def) {
    const auto q = path.find(key + "=");
    if (q == std::string::npos) return def;
    std::string v = path.substr(q + key.size() + 1);
    const auto amp = v.find('&');
    if (amp != std::string::npos) v = v.substr(0, amp);
    const auto sp = v.find(' ');
    if (sp != std::string::npos) v = v.substr(0, sp);
    return v;
}

std::string handle_tcp_line(const std::string& line) {
    if (line == "PING") return "PONG\n";
    if (line.rfind("REGISTER ", 0) == 0) {
        const auto rest = line.substr(9);
        const auto sp = rest.find(' ');
        if (sp == std::string::npos) return "ERR bad register\n";
        const auto sid = rest.substr(0, sp);
        const auto dev = rest.substr(sp + 1);
        std::lock_guard<std::mutex> lock(g_mu);
        g_sessions[sid] = dev;
        return "OK registered\n";
    }
    if (line == "LIST") {
        std::lock_guard<std::mutex> lock(g_mu);
        std::string out = "OK count=" + std::to_string(g_sessions.size()) + "\n";
        for (const auto& kv : g_sessions) out += kv.first + "->" + kv.second + "\n";
        return out;
    }
    return "ERR unknown\n";
}

bool read_file(const std::string& path, std::vector<char>& out) {
    std::ifstream ifs(path, std::ios::binary);
    if (!ifs) return false;
    out.assign(std::istreambuf_iterator<char>(ifs), std::istreambuf_iterator<char>());
    return !out.empty();
}

void send_bytes(int cfd, const std::string& content_type, const std::vector<char>& bytes) {
    std::ostringstream hdr;
    hdr << "HTTP/1.1 200 OK\r\n"
        << "Content-Type: " << content_type << "\r\n"
        << "Content-Length: " << bytes.size() << "\r\n"
        << "Connection: close\r\n\r\n";
    const auto hs = hdr.str();
    write(cfd, hs.data(), hs.size());
    write(cfd, bytes.data(), bytes.size());
    close(cfd);
}

void handle_http_client(int cfd) {
    char buf[2048];
    const ssize_t n = read(cfd, buf, sizeof(buf) - 1);
    if (n <= 0) {
        close(cfd);
        return;
    }
    buf[n] = '\0';
    std::string req(buf);
    std::string path = "/";
    {
        const auto sp1 = req.find(' ');
        const auto sp2 = req.find(' ', sp1 + 1);
        if (sp1 != std::string::npos && sp2 != std::string::npos) {
            path = req.substr(sp1 + 1, sp2 - sp1 - 1);
        }
    }

    std::string status = "200 OK";
    std::string content_type = "text/plain; charset=utf-8";
    std::string body = "ok\n";

    if (path == "/health") {
        body = "{\"service\":\"media_gateway\",\"status\":\"ok\"}\n";
        content_type = "application/json";
    } else if (path.rfind("/preview", 0) == 0) {
        const std::string device = query_param(path, "device", "edge-sim-001");
        const std::string jpg = g_preview_root + "/" + device + "/latest.jpg";
        std::vector<char> bytes;
        if (read_file(jpg, bytes)) {
            send_bytes(cfd, "image/jpeg", bytes);
            return;
        }
        status = "404 Not Found";
        body = "preview not found: " + jpg + "\n";
    } else if (path.rfind("/vod", 0) == 0) {
        const std::string session = query_param(path, "session", "");
        if (session.empty() || session.find("..") != std::string::npos || session.find('/') != std::string::npos) {
            status = "400 Bad Request";
            body = "need session=...\n";
        } else {
            const std::string mp4 = g_session_root + "/" + session + "/cam0/preview.mp4";
            std::vector<char> bytes;
            if (read_file(mp4, bytes)) {
                send_bytes(cfd, "video/mp4", bytes);
                return;
            }
            status = "404 Not Found";
            body = "vod not found: " + mp4 + "\n";
        }
    } else {
        status = "404 Not Found";
        body = "not found\n";
    }

    std::ostringstream resp;
    resp << "HTTP/1.1 " << status << "\r\n"
         << "Content-Type: " << content_type << "\r\n"
         << "Content-Length: " << body.size() << "\r\n"
         << "Connection: close\r\n\r\n"
         << body;
    const auto s = resp.str();
    write(cfd, s.data(), s.size());
    close(cfd);
}

void tcp_loop(int port) {
    emp::Logger log("media_gateway_tcp");
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    listen(fd, 16);
    log.info("TCP 监听 :" + std::to_string(port));
    while (true) {
        int cfd = accept(fd, nullptr, nullptr);
        if (cfd < 0) continue;
        char buf[512];
        const ssize_t n = read(cfd, buf, sizeof(buf) - 1);
        if (n > 0) {
            buf[n] = '\0';
            std::string line(buf);
            while (!line.empty() && (line.back() == '\n' || line.back() == '\r')) line.pop_back();
            const std::string resp = handle_tcp_line(line);
            write(cfd, resp.data(), resp.size());
        }
        close(cfd);
    }
}

void http_loop(int port) {
    emp::Logger log("media_gateway_http");
    int fd = ::socket(AF_INET, SOCK_STREAM, 0);
    int yes = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);
    bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    listen(fd, 32);
    log.info("HTTP 预览/VOD 监听 :" + std::to_string(port));
    while (true) {
        int cfd = accept(fd, nullptr, nullptr);
        if (cfd < 0) continue;
        std::thread(handle_http_client, cfd).detach();
    }
}

}  // namespace

int main(int argc, char** argv) {
    emp::Logger log("media_gateway");
    if (const char* root = std::getenv("EMP_PREVIEW_ROOT")) {
        g_preview_root = root;
    }
    if (const char* sroot = std::getenv("EMP_SESSION_ROOT")) {
        g_session_root = sroot;
    }
    const int tcp_port = 9100;
    const int http_port = 9101;
    std::thread(tcp_loop, tcp_port).detach();
    http_loop(http_port);
    return 0;
}
