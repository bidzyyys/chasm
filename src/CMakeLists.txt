
### LIBRARIES
# primitives
# TODO: commented for now as primitives is a header only library (this may change)
#file(GLOB_RECURSE PRIMITIVES_SOURCES "chasm/primitives/*.cpp")
#add_library(primitives ${PRIMITIVES_SOURCES})

### EXECUTABLES
add_executable(chasm main.cpp)
#target_link_libraries(chasm primitives) TODO

