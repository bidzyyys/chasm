
### LIBRARIES

# primitives
file(GLOB_RECURSE PRIMITIVES_SOURCES "chasm/primitives/*.cpp")
add_library(primitives ${PRIMITIVES_SOURCES})

# serialization
file(GLOB_RECURSE SERIALIZATION_SOURCES "chasm/serialization/*.cpp")
add_library(serialization ${SERIALIZATION_SOURCES})

# tokens
file(GLOB_RECURSE SUPPORTED_TOKENS_SOURCES "chasm/tokens/*.cpp")
add_library(supported_tokens ${SUPPORTED_TOKENS_SOURCES})

# database
file(GLOB_RECURSE DATABASE_SOURCES "chasm/db/*.cpp")
add_library(database ${DATABASE_SOURCES})
target_link_libraries(database ${LevelDB_LIBRARY})

### EXECUTABLES
add_executable(chasm main.cpp)
target_link_libraries(chasm primitives serialization ${OPENSSL_CRYPTO_LIBRARY})

