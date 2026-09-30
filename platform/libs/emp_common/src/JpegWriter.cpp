/**
 * @file JpegWriter.cpp
 * @brief libjpeg 封装写文件 + 测试图案
 */
#include "emp/JpegWriter.h"

#include <cstdio>
#include <jpeglib.h>

namespace emp {

bool write_jpeg_file(const std::string& path, int width, int height,
                     const std::vector<unsigned char>& rgb, int quality) {
    if (width <= 0 || height <= 0) {
        return false;
    }
    if (rgb.size() < static_cast<size_t>(width) * static_cast<size_t>(height) * 3) {
        return false;
    }
    FILE* fp = std::fopen(path.c_str(), "wb");
    if (!fp) {
        return false;
    }
    jpeg_compress_struct cinfo{};
    jpeg_error_mgr jerr{};
    cinfo.err = jpeg_std_error(&jerr);
    jpeg_create_compress(&cinfo);
    jpeg_stdio_dest(&cinfo, fp);
    cinfo.image_width = width;
    cinfo.image_height = height;
    cinfo.input_components = 3;
    cinfo.in_color_space = JCS_RGB;
    jpeg_set_defaults(&cinfo);
    jpeg_set_quality(&cinfo, quality, TRUE);
    jpeg_start_compress(&cinfo, TRUE);
    while (cinfo.next_scanline < cinfo.image_height) {
        JSAMPROW row = const_cast<JSAMPROW>(
            &rgb[static_cast<size_t>(cinfo.next_scanline) * static_cast<size_t>(width) * 3]);
        jpeg_write_scanlines(&cinfo, &row, 1);
    }
    jpeg_finish_compress(&cinfo);
    jpeg_destroy_compress(&cinfo);
    std::fclose(fp);
    return true;
}

std::vector<unsigned char> make_test_pattern_rgb(int width, int height, unsigned long long frame_id) {
    std::vector<unsigned char> rgb(static_cast<size_t>(width) * static_cast<size_t>(height) * 3);
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const size_t i = (static_cast<size_t>(y) * static_cast<size_t>(width) + static_cast<size_t>(x)) * 3;
            rgb[i + 0] = static_cast<unsigned char>((x + static_cast<int>(frame_id * 3)) % 256);
            rgb[i + 1] = static_cast<unsigned char>((y + static_cast<int>(frame_id * 5)) % 256);
            rgb[i + 2] = static_cast<unsigned char>((x + y + static_cast<int>(frame_id)) % 256);
        }
    }
    return rgb;
}

}  // namespace emp
