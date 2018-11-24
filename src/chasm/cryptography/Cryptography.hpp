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

    const unsigned int SUCCSESS = 1;

    const unsigned int VALID = 1;

    const unsigned int INVALID = 0;

    const unsigned int HASH256 = 32;

    const unsigned int PRIV_KEY = 32;

    const unsigned int PUB_KEY = 33;

    using evp_md_ctx_t = std::unique_ptr<EVP_MD_CTX, void (*)(EVP_MD_CTX *)>;

    using evp_pkey_ctx_t = std::unique_ptr<EVP_PKEY_CTX, void (*)(EVP_PKEY_CTX *)>;

    using evp_pkey_t = std::unique_ptr<EVP_PKEY, void (*)(EVP_PKEY *)>;

    using ec_key_t = std::unique_ptr<EC_KEY, void(*)(EC_KEY *)>;

    using bn_ctx_t = std::unique_ptr<BN_CTX, void(*)(BN_CTX *)>;

    using bignum_t = std::unique_ptr<BIGNUM, void(*)(BIGNUM *)>;

    using ec_group_t = std::unique_ptr<EC_GROUP, void(*)(EC_GROUP *)>;

    using ec_point_t = std::unique_ptr<EC_POINT, void(*)(EC_POINT *)>;

    using bn_ctx_t = std::unique_ptr<BN_CTX, void(*)(BN_CTX *)>;

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

        signature_t createSignature(const priv_key_t &priv_key,
                                    const bytes_t &data) const;

        bool isValidSignature(const pub_key_t &pub_key, const signature_t &signature,
                              const bytes_t &data) const;

        template <typename T>
        static bytes_t toBytes(T const& data) {

            bytes_t bytes(data.size());

            for(std::size_t i = 0; i < data.size(); ++i){
                bytes[i] = static_cast<std::byte>(data[i]);
            }

            return bytes;
        }

        template <typename T>
        static std::string bytesToHexString(T const& data) {

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
        static std::array<std::byte, SIZE> toByteArray(const std::array<unsigned char, SIZE>& collection) {

            std::array<std::byte, SIZE> array;

            for(std::size_t i = 0; i < SIZE; ++i) {
                array[i] = static_cast<std::byte>(collection[i]);
            }

            return array;
        }

        template <typename T>
        static std::vector<unsigned char> toUCharVector(T const& collection) {

            std::vector<unsigned char> bytes;

            for(std::size_t i = 0; i < collection.size(); ++i) {
                bytes.emplace_back(static_cast<unsigned char>(collection[i]));
            }

            return bytes;
        }


        bool validateSignature(const ec_key_t &pkey, const std::vector<unsigned char> &dgst,
                               const std::vector<unsigned char> &sign) const;

        signature_t getSignature(const bytes_t &data, const ec_key_t &pkey) const;
    };
}

#endif //CHASM_OPENSSL_H
