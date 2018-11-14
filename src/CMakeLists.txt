
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

# cryptography
file(GLOB_RECURSE CRYPTOGRAPHY_SOURCES "chasm/cryptography/*.cpp")
add_library(cryptography ${CRYPTOGRAPHY_SOURCES})
target_link_libraries(cryptography ${OPENSSL_CRYPTO_LIBRARY})

### EXECUTABLES
add_executable(chasm main.cpp)
target_link_libraries(chasm primitives serialization)

