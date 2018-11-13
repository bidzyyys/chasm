//
// Created by Daniel Bigos on 13.11.18.
//

#ifndef CHASM_OPENSSL_H
#define CHASM_OPENSSL_H

#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <array>
#include <cstddef>

namespace chasm::cryptography {

    const unsigned int HASH256 = 32;
    using hash256_t = std::array<std::byte, HASH256>;

    /*!
     * \brief OpenSSL wrapper
     */
    class OpenSSL {
    public:
        explicit OpenSSL() = default;

        virtual ~OpenSSL() = default;

        template <typename T>
        hash256_t sha256(T const &collection){
            return hash256_t();
        }
        hash256_t test();

    private:

    };
}

#endif //CHASM_OPENSSL_H
