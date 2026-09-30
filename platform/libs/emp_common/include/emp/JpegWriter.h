/**
 * @file JpegWriter.h
 * @brief 将 RGB888 缓冲写成 JPEG 文件（企业预览链路用）
 */
#pragma once
#include <string>
#include <vector>

namespace emp {

/**
 * @brief 写一张 JPEG
 * @param path 输出路径
 * @param width 宽
 * @param height 高
 * @param rgb 长度 width*height*3，行优先 RGB
 * @param quality 1-100
 * @return true 成功
 */
bool write_jpeg_file(const std::string& path, int width, int height,
                     const std::vector<unsigned char>& rgb, int quality = 80);

/**
 * @brief 生成教学用渐变测试图案 RGB
 */
std::vector<unsigned char> make_test_pattern_rgb(int width, int height, unsigned long long frame_id);

}  // namespace emp
