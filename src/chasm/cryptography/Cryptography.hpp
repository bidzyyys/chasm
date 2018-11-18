//
// Created by Daniel Bigos on 13.11.18.
//

#ifndef CHASM_OPENSSL_H
#define CHASM_OPENSSL_H

#include <iostream>
#include <iomanip>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/bn.h>
#include "chasm/types.hpp"

namespace chasm::cryptography {

    const unsigned int HASH256 = 32;
    const unsigned int PRIV_KEY = 32;
    const unsigned int PUB_KEY_UNCOMPRESSED = 65;
    const unsigned int PUB_KEY = 33;

    using evp_md_ctx_t = std::unique_ptr<EVP_MD_CTX, void (*)(EVP_MD_CTX *)>;

    using evp_pkey_ctx_t = std::unique_ptr<EVP_PKEY_CTX, void (*)(EVP_PKEY_CTX *)>;

    using evp_pkey_t = std::unique_ptr<EVP_PKEY, void (*)(EVP_PKEY *)>;

    using ec_key_t = std::unique_ptr<EC_KEY, void(*)(EC_KEY *)>;

    using bn_ctx_t = std::unique_ptr<BN_CTX, void(*)(BN_CTX *)>;

    using pub_key_uncompressed_t = std::array<unsigned char, PUB_KEY_UNCOMPRESSED>;

    /*!
     * \brief Cryptography Library exception
     */
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

        chasm::types::key_pair_t generateECDHKeyPair() const;

        template <typename T>
        std::vector<std::byte> toBytes(T const& data) const {

            std::vector<std::byte> bytes(data.size());

            for(std::size_t i = 0; i < data.size(); ++i){
                bytes[i] = static_cast<std::byte>(data[i]);
            }

            return bytes;
        }

        template <typename T>
        std::string bytesToHexString(T const& data) const {

            std::stringstream ss;

            for(size_t i = 0; i < data.size(); ++i) {
                ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(data[i]);
            }

            return ss.str();
        }

    private:
        const std::string getOpenSSLError() const;

        evp_md_ctx_t newEVP_MD_CTX() const;

        static void freeEVP_MD_CTX(EVP_MD_CTX *evp_md_ctx);

        evp_pkey_ctx_t newEVP_PKEY_CTX(EVP_PKEY *evp_pkey, ENGINE *engine) const;

        evp_pkey_ctx_t newEVP_PKEY_CTX(int key_type, ENGINE *engine) const;

        static void freeEVP_PKEY_CTX(EVP_PKEY_CTX *evp_pkey_ctx);

        static void freeEVP_PKEY(EVP_PKEY *evp_pkey);

        static void freeEC_KEY(EC_KEY *ec_key);

        static void freeBN_CTX(BN_CTX *bn_ctx);

        bn_ctx_t getBN_CTX() const;

        evp_pkey_t generateECDHParams() const;

        evp_pkey_t genEVP_PKEY(evp_pkey_ctx_t &evp_pkey_ctx) const;

        void initKeyGeneration(evp_pkey_ctx_t &evp_pkey_ctx) const;

        evp_pkey_t keygen(evp_pkey_ctx_t &evp_pkey_ctx) const;

        evp_pkey_t createECDHParams(evp_pkey_ctx_t &evp_pkey_ctx) const;

        evp_md_ctx_t initEVP_MD_CTX(const EVP_MD *evp_md, ENGINE *engine = nullptr) const;

        evp_pkey_ctx_t initEVP_PKEY_CTX(EVP_PKEY *evp_pkey, ENGINE *engine = nullptr) const;

        evp_pkey_ctx_t initEVP_PKEY_CTX(int key_type, ENGINE *engine = nullptr) const;

        chasm::types::hash_t getSHA256(evp_md_ctx_t &evp_md_ctx) const;

        void initECDHParamsGeneration(evp_pkey_ctx_t &evp_pkey_ctx) const;

        void setECDHParamgenCurve(evp_pkey_ctx_t &evp_pkey_ctx, int nid) const;

        chasm::types::key_pair_t createECDHKey(evp_pkey_t &params) const;

        chasm::types::key_pair_t extractECDHKeyPair(evp_pkey_t &pkey) const;

        ec_key_t getECkeyfromEVP(evp_pkey_t &pkey) const;

        chasm::types::priv_key_t getPrivateKey(ec_key_t &ec_key) const;

        chasm::types::pub_key_t getPublicKey(ec_key_t &ec_key) const;

        chasm::types::pub_key_t compressPublicKey(const pub_key_uncompressed_t &pub_key_uncompressed) const;

        point_conversion_form_t getPointConversion(const EC_GROUP *ec_group) const;

        const EC_GROUP * getEC_GROUP(ec_key_t &ec_key) const;

        const EC_POINT * getEC_POINT(ec_key_t &ec_key) const;

        const BIGNUM * getBIGNUM(ec_key_t &ec_key) const;

        template <typename T>
        void updateEVPDigest(evp_md_ctx_t &evp_ctx, T const &data) const {

            if (EVP_DigestUpdate(evp_ctx.get(), &data[0],  static_cast<int>(data.size())) != 1) {
                throw CryptographyError("Unexpected error while updating EVP, " + getOpenSSLError());
            }
        }

        template <typename T>
        unsigned int finishEVPDigiest(evp_md_ctx_t &evp_ctx, T &output) const {
            unsigned int length = 0;

            if (EVP_DigestFinal_ex(evp_ctx.get(), &output[0], &length) != 1) {
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
