/**
 * @file ringbuffer_demo.cpp
 * @brief 环形缓冲练习：推入覆盖后弹出验证
 */
#include "emp/Logger.h"
#include "emp/RingBuffer.h"
#include <cassert>

int main() {
    emp::Logger log("lab_ring");
    emp::RingBuffer<int> rb(3);
    rb.push_overwrite(1);
    rb.push_overwrite(2);
    rb.push_overwrite(3);
    rb.push_overwrite(4);  // 覆盖 1
    assert(rb.size() == 3);
    assert(rb.pop().value() == 2);
    assert(rb.pop().value() == 3);
    assert(rb.pop().value() == 4);
    log.info("ringbuffer demo OK");
    return 0;
}
