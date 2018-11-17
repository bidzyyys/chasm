//
// Created by Daniel Bigos on 13.11.18.
//

#include <iostream>
#include <memory>
#include "Cryptography.hpp"

using namespace chasm::cryptography;
using namespace chasm::types;

CryptographyError::CryptographyError(const std::string &error_msg)
        : std::runtime_error(error_msg) {}

hash_t Cryptography::sha256(const std::vector<std::byte> &data) const {

    try {
        evp_md_ctx_t evp_md_ctx = initEVP_MD_CTX(EVP_sha256());

        updateEVPDigest(evp_md_ctx, data);

        return getSHA256(evp_md_ctx);
    }
    catch(CryptographyError &e) {
        throw CryptographyError(std::string("Cryptography: ") + e.what());
    }
}

chasm::types::hash_t Cryptography::getSHA256(evp_md_ctx_t &evp_md_ctx) const {

    std::array<unsigned char, HASH256> output{};

    if(finishEVPDigiest(evp_md_ctx, output) != HASH256) {
        throw CryptographyError("Unexpected length of hash");
    }

    return toByteArray(output);
}

evp_md_ctx_t Cryptography::newEVP_MD_CTX() const {

    auto evp_md_ctx = EVP_MD_CTX_new();

    if(evp_md_ctx == nullptr) {
        throw CryptographyError("Unexpected error while creating EVP_MD_CTX, " + getOpenSSLError());
    }

    return evp_md_ctx_t(evp_md_ctx, &freeEVP_MD_CTX);
}

void Cryptography::freeEVP_MD_CTX(EVP_MD_CTX *evp_md_ctx) {

    EVP_MD_CTX_free(evp_md_ctx);
}

evp_md_ctx_t Cryptography::initEVP_MD_CTX(const EVP_MD *evp_md, ENGINE *engine) const {

    if (evp_md == nullptr) {
        throw CryptographyError("Unexpected error while initializing EVP_MD_CTX, EVP_MD cannot be null");
    }

    auto evp_ctx = newEVP_MD_CTX();

    if (EVP_DigestInit_ex(evp_ctx.get(), evp_md, engine) != 1) {
        throw CryptographyError("Unexpected error while initializing EVP_MD_CTX, " + getOpenSSLError());
    }

    return evp_ctx;
}

const std::string Cryptography::getOpenSSLError() const {

    return "error code: " + std::to_string(ERR_get_error());
}

void Cryptography::freeEVP_PKEY_CTX(EVP_PKEY_CTX *evp_pkey_ctx) {

    EVP_PKEY_CTX_free(evp_pkey_ctx);
}

evp_pkey_ctx_t Cryptography::newEVP_PKEY_CTX(EVP_PKEY *evp_pkey, ENGINE *engine) const {

    auto evp_pkey_ctx = EVP_PKEY_CTX_new(evp_pkey, engine);

    if (evp_pkey_ctx == nullptr) {
        throw CryptographyError("Unexpected error while creating EVP_PKEY_CTX, " + getOpenSSLError());
    }

    return evp_pkey_ctx_t(evp_pkey_ctx, &freeEVP_PKEY_CTX);
}

evp_pkey_ctx_t Cryptography::newEVP_PKEY_CTX(int key_type, ENGINE *engine) const {

    auto evp_pkey_ctx = EVP_PKEY_CTX_new_id(key_type, engine);

    if (evp_pkey_ctx == nullptr) {
        throw CryptographyError("Unexpected error while creating EVP_PKEY_CTX, " + getOpenSSLError());
    }

    return evp_pkey_ctx_t(evp_pkey_ctx, &freeEVP_PKEY_CTX);
}

evp_pkey_ctx_t Cryptography::initEVP_PKEY_CTX(EVP_PKEY *evp_pkey, ENGINE *engine) const {

    if (evp_pkey == nullptr) {
        throw CryptographyError("Unexpected error while initializing EVP, EVP_MD cannot be null");
    }

    auto evp_pkey_ctx = newEVP_PKEY_CTX(evp_pkey, engine);

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != 1) {
        throw CryptographyError("Unexpected error while initializing EVP, " + getOpenSSLError());
    }

    return evp_pkey_ctx;
}

evp_pkey_ctx_t Cryptography::initEVP_PKEY_CTX(int key_type, ENGINE *engine) const {

    auto evp_pkey_ctx = newEVP_PKEY_CTX(key_type, engine);

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != 1) {
        throw CryptographyError("Unexpected error while initializing EVP, " + getOpenSSLError());
    }

    return evp_pkey_ctx;
}

key_pair_t Cryptography::generateECDHKeyPair() const {

    try {
        auto pkey_param = generateECDHParams();

        return createECDHKey(pkey_param);
    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("Cryptography: ") + e.what());
    }
}

void Cryptography::freeEVP_PKEY(EVP_PKEY *evp_pkey) {

    EVP_PKEY_free(evp_pkey);
}

evp_pkey_t Cryptography::generateECDHParams() const {

    try {
        auto evp_pkey_ctx = initEVP_PKEY_CTX(EVP_PKEY_EC);

        initECDHParamsGeneration(evp_pkey_ctx);

        setECDHParamgenCurve(evp_pkey_ctx, NID_X9_62_prime256v1);

        return createECDHParams(evp_pkey_ctx);
    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("ECDH params generation: ") + e.what());
    }
}

void Cryptography::initECDHParamsGeneration(evp_pkey_ctx_t &evp_pkey_ctx) const {

    if (EVP_PKEY_paramgen_init(evp_pkey_ctx.get()) != 1) {
        throw CryptographyError("Unexpected error while initializing params generation for ECDH, " + getOpenSSLError());
    }
}

void Cryptography::setECDHParamgenCurve(evp_pkey_ctx_t &evp_pkey_ctx, int nid) const {

    if (EVP_PKEY_CTX_set_ec_paramgen_curve_nid(evp_pkey_ctx.get(), nid) != 1) {
        throw CryptographyError("Unexpected error while setting curve for ECDH, " + getOpenSSLError());
    }
}

evp_pkey_t Cryptography::createECDHParams(evp_pkey_ctx_t &evp_pkey_ctx) const {

    EVP_PKEY *params = nullptr;

    if (EVP_PKEY_paramgen(evp_pkey_ctx.get(), &params) == 0 || params == nullptr) {
        throw CryptographyError("Unexpected error while creating params for ECDH, " + getOpenSSLError());
    }

    return evp_pkey_t(params, &freeEVP_PKEY);
}

key_pair_t Cryptography::createECDHKey(evp_pkey_t &params) const {

    try {
        auto evp_pkey_ctx = initEVP_PKEY_CTX(params.get());

        auto pkey = genPKey(evp_pkey_ctx);

        // TODO
        // get keys from pkey and convert them to std::byte representation

        return key_pair_t();
    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("ECDH key generation: ") + e.what());
    }
}

evp_pkey_t Cryptography::genPKey(evp_pkey_ctx_t &evp_pkey_ctx) const {

    initKeyGeneration(evp_pkey_ctx);

    return keygen(evp_pkey_ctx);
}

void Cryptography::initKeyGeneration(evp_pkey_ctx_t &evp_pkey_ctx) const {

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != 1) {
        throw CryptographyError("Unexpected error while initializing keygen for ECDH, " + getOpenSSLError());
    }
}

evp_pkey_t Cryptography::keygen(evp_pkey_ctx_t &evp_pkey_ctx) const {

    EVP_PKEY *pkey = nullptr;

    if (EVP_PKEY_keygen(evp_pkey_ctx.get(), &pkey) != 1 || pkey == nullptr) {
        throw CryptographyError("Unexpected error while keygeneration for ECDH, " + getOpenSSLError());
    }

    return evp_pkey_t(pkey, &freeEVP_PKEY);
}













