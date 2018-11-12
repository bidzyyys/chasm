
### LIBRARIES

# primitives
file(GLOB_RECURSE PRIMITIVES_SOURCES "chasm/primitives/*.cpp")
add_library(primitives ${PRIMITIVES_SOURCES})

# serialization
file(GLOB_RECURSE SERIALIZATION_SOURCES "chasm/serialization/*.cpp")
add_library(serialization ${SERIALIZATION_SOURCES})

# supported_tokens
file(GLOB_RECURSE SUPPORTED_TOKENS_SOURCES "chasm/common/supported_tokens/*.cpp")
add_library(supported_tokens ${SUPPORTED_TOKENS_SOURCES})


### EXECUTABLES
add_executable(chasm main.cpp)
target_link_libraries(chasm primitives serialization)

