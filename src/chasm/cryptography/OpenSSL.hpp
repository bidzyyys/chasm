//
// Created by Daniel Bigos on 13.11.18.
//

#ifndef CHASM_OPENSSL_H
#define CHASM_OPENSSL_H

#include <openssl/sha.h>
#include <array>
#include <cstddef>

namespace chasm::cryptography {

    using hash256_t = std::array<std::byte, SHA256_DIGEST_LENGTH>;

    /*!
     * \brief Basic transaction
     */
    class OpenSSL {
    public:
        explicit OpenSSL() = default;

        virtual ~OpenSSL() = default;

        template <typename T>
        hash256_t generateSHA256(T const& collection){
            return hash256_t();
        }
    private:

    };
}

#endif //CHASM_OPENSSL_H
