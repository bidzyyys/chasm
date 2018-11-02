cmake_minimum_required(VERSION 3.12)
project(chasm)

set(CMAKE_CXX_STANDARD 17)
if(UNIX AND NOT APPLE)
    set(CMAKE_CXX_FLAGS "-pthread")
endif()

find_package(Boost 1.67 REQUIRED COMPONENTS unit_test_framework)

include_directories(src/)
include_directories(${Boost_INCLUDE_DIRS})


add_subdirectory(src/)
add_subdirectory(tests/)
