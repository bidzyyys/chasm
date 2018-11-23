cmake_minimum_required(VERSION 3.7)
project(chasm)

set(CMAKE_CXX_STANDARD 17)
if (UNIX AND NOT APPLE)
    set(CMAKE_CXX_FLAGS "-pthread")
endif ()

set(CMAKE_CXX_FLAGS "-Werror -pedantic")

find_package(Boost 1.67 REQUIRED COMPONENTS unit_test_framework)
find_package(OpenSSL 1.0 REQUIRED COMPONENTS Crypto)

include_directories(src/)
include_directories(${Boost_INCLUDE_DIRS})
include_directories(${OPENSSL_INCLUDE_DIR})

add_subdirectory(src/)

add_subdirectory(tests/)
