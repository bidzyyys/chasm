cmake_minimum_required(VERSION 3.7)
project(chasm)

set(CMAKE_CXX_STANDARD 17)
if(UNIX AND NOT APPLE)
    set(CMAKE_CXX_FLAGS "-pthread")
endif()

set(CMAKE_CXX_FLAGS "-Werror -pedantic")

find_package(Boost 1.62 REQUIRED COMPONENTS unit_test_framework serialization)

include_directories(src/)
include_directories(${Boost_INCLUDE_DIRS})


add_subdirectory(src/)

enable_testing()
add_subdirectory(tests/)
