
### LIBRARIES

# primitives
file(GLOB_RECURSE PRIMITIVES_SOURCES "chasm/primitives/*.cpp")
add_library(primitives ${PRIMITIVES_SOURCES})

# serialization
file(GLOB_RECURSE SERIALIZATION_SOURCES "chasm/serialization/*.cpp")
add_library(serialization ${SERIALIZATION_SOURCES})


### EXECUTABLES
add_executable(chasm main.cpp)
target_link_libraries(chasm primitives serialization)

