/**
 * @file RingBuffer.h
 * @brief 定长环形缓冲（教学用，非无锁）
 * 内容：演示音视频常用数据结构；对应 labs/data_structures
 */
#pragma once
#include <cstddef>
#include <mutex>
#include <optional>
#include <vector>

namespace emp {

template <typename T>
class RingBuffer {
public:
    /** @brief 构造指定容量的环缓 */
    explicit RingBuffer(std::size_t capacity)
        : buf_(capacity), capacity_(capacity), head_(0), tail_(0), size_(0) {}

    /** @brief 推入；满则覆盖最旧（背压策略：丢旧保新） */
    void push_overwrite(const T& item) {
        std::lock_guard<std::mutex> lock(mu_);
        buf_[head_] = item;
        head_ = (head_ + 1) % capacity_;
        if (size_ < capacity_) {
            ++size_;
        } else {
            tail_ = (tail_ + 1) % capacity_;  // 覆盖时尾指针前移
        }
    }

    /** @brief 弹出最旧元素；空则 nullopt */
    std::optional<T> pop() {
        std::lock_guard<std::mutex> lock(mu_);
        if (size_ == 0) {
            return std::nullopt;
        }
        T item = buf_[tail_];
        tail_ = (tail_ + 1) % capacity_;
        --size_;
        return item;
    }

    /** @brief 当前元素个数 */
    std::size_t size() const {
        std::lock_guard<std::mutex> lock(mu_);
        return size_;
    }

private:
    std::vector<T> buf_;
    std::size_t capacity_;
    std::size_t head_;
    std::size_t tail_;
    std::size_t size_;
    mutable std::mutex mu_;
};

}  // namespace emp
