/**
 * @file hello_types.cpp
 * @brief C++ 语法练习：Types 与 Logger
 */
#include "emp/Logger.h"
#include "emp/Types.h"
#include <iostream>

int main() {
    emp::Logger log("lab_syntax");
    emp::DeviceCode code = "edge-sim-001";
    log.info(std::string("device=") + code + " now_ns=" + std::to_string(emp::now_ns()));
    return 0;
}
