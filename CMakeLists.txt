cmake_minimum_required(VERSION 3.16)
project(eo_edge_media_platform LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
find_package(Threads REQUIRED)

set(EMP_COMMON_DIR ${CMAKE_SOURCE_DIR}/platform/libs/emp_common)

add_library(emp_common STATIC
  ${EMP_COMMON_DIR}/src/Logger.cpp
  ${EMP_COMMON_DIR}/src/PluginLoader.cpp
  ${EMP_COMMON_DIR}/src/JpegWriter.cpp
)
target_include_directories(emp_common PUBLIC ${EMP_COMMON_DIR}/include)
target_link_libraries(emp_common PUBLIC dl jpeg)

# Virtual 相机插件
add_library(emp_cam_Virtual SHARED
  platform/services/edge_agent/plugins/Virtual/VirtualCamera.cpp
)
target_include_directories(emp_cam_Virtual PRIVATE ${EMP_COMMON_DIR}/include)
set_target_properties(emp_cam_Virtual PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
  OUTPUT_NAME emp_cam_Virtual
)

# V4L2 占位插件（RK3588 前可用 Stub）
add_library(emp_cam_V4L2_Stub SHARED
  platform/services/edge_agent/plugins/V4L2_Stub/V4l2StubCamera.cpp
)
target_include_directories(emp_cam_V4L2_Stub PRIVATE ${EMP_COMMON_DIR}/include)
set_target_properties(emp_cam_V4L2_Stub PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
  OUTPUT_NAME emp_cam_V4L2_Stub
)

add_executable(edge_agent platform/services/edge_agent/src/main.cpp)
target_link_libraries(edge_agent PRIVATE emp_common)
set_target_properties(edge_agent PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(media_gateway platform/services/media_gateway/src/main.cpp)
target_link_libraries(media_gateway PRIVATE emp_common Threads::Threads)
set_target_properties(media_gateway PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# labs
add_executable(lab_ringbuffer labs/data_structures/ringbuffer_demo.cpp)
target_link_libraries(lab_ringbuffer PRIVATE emp_common)
set_target_properties(lab_ringbuffer PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

add_executable(lab_syntax labs/cpp_syntax/hello_types.cpp)
target_link_libraries(lab_syntax PRIVATE emp_common)
set_target_properties(lab_syntax PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

enable_testing()
add_test(NAME lab_ringbuffer COMMAND lab_ringbuffer)
add_test(NAME lab_syntax COMMAND lab_syntax)
