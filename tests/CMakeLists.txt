### EXECUTABLES

# all

file(GLOB_RECURSE TEST_SOURCES "*.cpp")
add_executable(all_unit_tests ${TEST_SOURCES})
target_include_directories(all_unit_tests PRIVATE ${Boost_INCLUDE_DIRS})
target_link_libraries(all_unit_tests ${Boost_LIBRARIES} primitives)

# serialization
add_executable(serialization_unit_tests main_test.cpp chasm/serialization/PrimitivesTests.cpp)
target_link_libraries(serialization_unit_tests ${Boost_LIBRARIES})

