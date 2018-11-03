### EXECUTABLES

# all

file(GLOB_RECURSE TEST_SOURCES "*.cpp")
add_executable(all_unit_tests ${TEST_SOURCES})
target_include_directories(all_unit_tests PRIVATE ${Boost_INCLUDE_DIRS})
target_link_libraries(all_unit_tests ${Boost_LIBRARIES})

add_test(all all_unit_tests)
add_test(NAME primitives_tests COMMAND all_unit_tests -t primitives)



