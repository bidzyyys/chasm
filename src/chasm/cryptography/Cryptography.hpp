//
// Created by Daniel Bigos on 13.11.18.
//

#ifndef CHASM_OPENSSL_H
#define CHASM_OPENSSL_H

#include <algorithm>
#include <functional>
#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/ec.h>
#include "chasm/types.hpp"

namespace chasm::cryptography {

    const unsigned int SUCCSESS = 1;

    const unsigned int VALID = 1;

    const unsigned int INVALID = 0;

    const unsigned int HASH256_SIZE = 32;

    const unsigned int PRIV_KEY_SIZE = 32;

    const unsigned int PUB_KEY_SIZE = 33;

    using evp_md_ctx_t = std::unique_ptr<EVP_MD_CTX, std::function<void(EVP_MD_CTX *)>>;

    using evp_pkey_ctx_t = std::unique_ptr<EVP_PKEY_CTX, std::function<void(EVP_PKEY_CTX *)>>;

    using evp_pkey_t = std::unique_ptr<EVP_PKEY, std::function<void(EVP_PKEY *)>>;

    using ec_key_t = std::unique_ptr<EC_KEY, std::function<void(EC_KEY *)>>;

    using bn_ctx_t = std::unique_ptr<BN_CTX, std::function<void(BN_CTX *)>>;

    using bignum_t = std::unique_ptr<BIGNUM, std::function<void(BIGNUM *)>>;

    using ec_group_t = std::unique_ptr<EC_GROUP, std::function<void(EC_GROUP *)>>;

    using ec_point_t = std::unique_ptr<EC_POINT, std::function<void(EC_POINT *)>>;

    using bn_ctx_t = std::unique_ptr<BN_CTX, std::function<void(BN_CTX *)>>;

    /*!
     * \brief Cryptography Library exception
     */
    class CryptographyError : public std::runtime_error {
    public:
        explicit CryptographyError(const std::string &error_msg);
    };

    /*!
     * \brief Cryptography Library
     * Wraps OpenSSL
     */
    class Cryptography {
    public:
        explicit Cryptography() = default;

        virtual ~Cryptography() = default;

        chasm::types::hash_t sha256(const bytes_t &data) const;

        chasm::types::key_pair_t generateECDHKeyPair() const;

        signature_t sign(const priv_key_t &priv_key,
                         const bytes_t &data) const;

        bool isValidSignature(const pub_key_t &pub_key, const signature_t &signature,
                              const bytes_t &data) const;

        template <typename T>
        static bytes_t toBytes(T const& data) {

            bytes_t bytes(data.size());

            std::transform(data.begin(), data.end(), bytes.begin(), [](const uint8_t &byte){return static_cast<std::byte>(byte);});

            return bytes;
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

        static void freeBIGNUM(BIGNUM *bignum);

        static void freeEC_POINT(EC_POINT *ec_point);

        static void freeEC_GROUP(EC_GROUP *ec_group);

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

        ec_key_t getEC_KEYfromEVP_PKEY(evp_pkey_t &pkey) const;

        chasm::types::priv_key_t getPrivateKey(ec_key_t &ec_key) const;

        chasm::types::pub_key_t getPublicKey(ec_key_t &ec_key) const;

        const EC_GROUP * getEC_GROUP(ec_key_t &ec_key) const;

        const EC_POINT * getEC_POINT(ec_key_t &ec_key) const;

        const BIGNUM * getBIGNUM(ec_key_t &ec_key) const;

        bignum_t getBIGNUMFromPrivKey(const priv_key_t &priv_key) const;

        bn_ctx_t createBN_CTX() const;

        ec_key_t getEC_KEYFromBIGNUM(const bignum_t &bignum, int nid) const;

        ec_key_t createEC_KEY(int nid, point_conversion_form_t point_conversion_form = POINT_CONVERSION_COMPRESSED) const;

        ec_key_t getEC_KEYFromPublicKey(const pub_key_t &pub_key, int nid) const;

        ec_key_t getEC_KEYFromPrivateKey(const priv_key_t &priv_key, int nid) const;

        ec_group_t createEC_GROUP(int nid) const;

        ec_point_t createEC_POINT(const ec_group_t & ec_group) const;

        ec_point_t getEC_POINTFromPublicKey(const pub_key_t &pub_key, int nid) const;

        template <typename T>
        void updateEVPDigest(evp_md_ctx_t &evp_ctx, T const &data) const {

            if (EVP_DigestUpdate(evp_ctx.get(), data.data(),  static_cast<int>(data.size())) != SUCCSESS) {
                throw CryptographyError("Unexpected error while updating EVP, " + getOpenSSLError());
            }
        }

        template <typename T>
        unsigned int finishEVPDigiest(evp_md_ctx_t &evp_ctx, T &output) const {

            unsigned int length = 0;

            if (EVP_DigestFinal_ex(evp_ctx.get(), output.data(), &length) != SUCCSESS) {
                throw CryptographyError("Unexpected error while finishing EVP, " + getOpenSSLError());
            }

            return length;
        }

        template<std::size_t SIZE>
        static std::array<std::byte, SIZE> toByteArray(const std::array<uint8_t, SIZE>& collection) {

            std::array<std::byte, SIZE> array;

            std::transform(collection.begin(), collection.end(), array.begin(), [](const uint8_t &byte){return static_cast<std::byte>(byte);});

            return array;
        }

        template <typename T>
        static std::vector<uint8_t> toUInt8Vector(T const &collection) {

            std::vector<uint8_t> bytes(collection.size());

            std::transform(collection.begin(), collection.end(), bytes.begin(), [](const std::byte &byte){return static_cast<uint8_t>(byte);});

            return bytes;
        }


        bool validateSignature(const ec_key_t &pkey, const std::vector<uint8_t> &dgst,
                               const std::vector<uint8_t> &sign) const;

        signature_t getSignature(const bytes_t &data, const ec_key_t &pkey) const;
    };
}

#endif //CHASM_OPENSSL_H
