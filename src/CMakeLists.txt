
### LIBRARIES
# primitives
file(GLOB_RECURSE PRIMITIVES_SOURCES "chasm/primitives/*.cpp")
add_library(primitives ${PRIMITIVES_SOURCES})

# dto
file(GLOB_RECURSE DTO_SOURCES "chasm/dto/*.cpp")
add_library(dto ${DTO_SOURCES})


### EXECUTABLES
add_executable(chasm main.cpp)
target_link_libraries(chasm primitives dto)

