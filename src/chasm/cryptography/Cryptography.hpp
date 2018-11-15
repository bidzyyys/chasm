//
// Created by Daniel Bigos on 13.11.18.
//

#ifndef CHASM_OPENSSL_H
#define CHASM_OPENSSL_H

#include <iostream>
#include <iomanip>
#include <openssl/err.h>
#include <openssl/evp.h>
#include "chasm/types.hpp"

namespace chasm::cryptography {

    const unsigned int HASH256 = 32;

    using evp_t = std::unique_ptr<EVP_MD_CTX, void (*)(EVP_MD_CTX *)>;

    class CryptographyError : public std::runtime_error {
    public:
        explicit CryptographyError(const std::string &error_msg);
    };

    /*!
     * \brief OpenSSL wrapper
     */
    class Cryptography {
    public:
        explicit Cryptography() = default;

        virtual ~Cryptography() = default;

        chasm::types::hash_t sha256(const std::vector<std::byte> &data) const;

        template <typename T>
        std::vector<std::byte> toBytes(T const& data){
            std::vector<std::byte> bytes(data.size());

            for(std::size_t i = 0; i < data.size(); ++i){
                bytes[i] = static_cast<std::byte>(data[i]);
            }

            return bytes;
        }

        template <typename T>
        std::string bytesToHexString(T const& data){
            std::stringstream ss;

            for(size_t i = 0; i < data.size(); ++i) {
                ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(data[i]);
            }

            return ss.str();
        }

    private:
        evp_t newEVP() const;

        static void freeEVP(EVP_MD_CTX *EVP);

        evp_t initEVP(const EVP_MD *evp_md, ENGINE *engine = nullptr) const;

        const std::string getOpenSSLError() const;

        template <typename T>
        void updateEVP(evp_t &EVP, T const &data) const {
            if (EVP_DigestUpdate(EVP.get(), &data[0],  static_cast<int>(data.size())) == 0) {
                throw CryptographyError("Unexpected error while updating EVP, " + getOpenSSLError());
            }
        }

        template <typename T>
        unsigned int finishEVP(evp_t &evp, T &output) const {
            unsigned int length = 0;

            if (EVP_DigestFinal_ex(evp.get(), &output[0], &length) == 0) {
                throw CryptographyError("Unexpected error while finishing EVP, " + getOpenSSLError());
            }

            return length;
        }

        template<std::size_t SIZE>
        std::array<std::byte, SIZE> toByteArray(const std::array<unsigned char, SIZE>& collection) const {
            std::array<std::byte, SIZE> array;
            for(std::size_t i = 0; i < SIZE; ++i) {
                array[i] = static_cast<std::byte>(collection[i]);
            }

            return array;
        }
    };
}

#endif //CHASM_OPENSSL_H
