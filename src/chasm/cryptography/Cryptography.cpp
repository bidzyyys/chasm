//
// Created by Daniel Bigos on 13.11.18.
//

#include <iostream>
#include <memory>
#include <openssl/crypto.h>
#include <openssl/ecdsa.h>
#include "Cryptography.hpp"
#include <utility>

using namespace chasm::cryptography;
using namespace chasm::types;

CryptographyError::CryptographyError(const std::string &error_msg)
        : std::runtime_error(error_msg) {}

hash_t Cryptography::sha256(const bytes_t &data) const {

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

    if (EVP_DigestInit_ex(evp_ctx.get(), evp_md, engine) != SUCCSESS) {
        throw CryptographyError("Unexpected error while EVP_DigestInit_ex, " + getOpenSSLError());
    }

    return evp_ctx;
}

const std::string Cryptography::getOpenSSLError() const {

    auto error = ERR_error_string(ERR_get_error(), nullptr);
    return std::string(error);
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

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while initializing EVP, " + getOpenSSLError());
    }

    return evp_pkey_ctx;
}

evp_pkey_ctx_t Cryptography::initEVP_PKEY_CTX(int key_type, ENGINE *engine) const {

    auto evp_pkey_ctx = newEVP_PKEY_CTX(key_type, engine);

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != SUCCSESS) {
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

    if (EVP_PKEY_paramgen_init(evp_pkey_ctx.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while initializing params generation for ECDH, " + getOpenSSLError());
    }
}

void Cryptography::setECDHParamgenCurve(evp_pkey_ctx_t &evp_pkey_ctx, int nid) const {

    if (EVP_PKEY_CTX_set_ec_paramgen_curve_nid(evp_pkey_ctx.get(), nid) != SUCCSESS) {
        throw CryptographyError("Unexpected error while setting curve for ECDH, " + getOpenSSLError());
    }
}

evp_pkey_t Cryptography::createECDHParams(evp_pkey_ctx_t &evp_pkey_ctx) const {

    EVP_PKEY *params = nullptr;

    if (EVP_PKEY_paramgen(evp_pkey_ctx.get(), &params) != SUCCSESS || params == nullptr) {
        throw CryptographyError("Unexpected error while creating params for ECDH, " + getOpenSSLError());
    }

    return evp_pkey_t(params, &freeEVP_PKEY);
}

key_pair_t Cryptography::createECDHKey(evp_pkey_t &params) const {

    try {
        auto evp_pkey_ctx = initEVP_PKEY_CTX(params.get());

        auto pkey = genEVP_PKEY(evp_pkey_ctx);

        return extractECDHKeyPair(pkey);
    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("ECDH key generation: ") + e.what());
    }
}

evp_pkey_t Cryptography::genEVP_PKEY(evp_pkey_ctx_t &evp_pkey_ctx) const {

    initKeyGeneration(evp_pkey_ctx);

    return keygen(evp_pkey_ctx);
}

void Cryptography::initKeyGeneration(evp_pkey_ctx_t &evp_pkey_ctx) const {

    if (EVP_PKEY_keygen_init(evp_pkey_ctx.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while initializing keygen for ECDH, " + getOpenSSLError());
    }
}

evp_pkey_t Cryptography::keygen(evp_pkey_ctx_t &evp_pkey_ctx) const {

    EVP_PKEY *pkey = nullptr;

    if (EVP_PKEY_keygen(evp_pkey_ctx.get(), &pkey) != SUCCSESS || pkey == nullptr) {
        throw CryptographyError("Unexpected error while keygeneration for ECDH, " + getOpenSSLError());
    }

    return evp_pkey_t(pkey, &freeEVP_PKEY);
}

key_pair_t Cryptography::extractECDHKeyPair(evp_pkey_t &pkey) const {

    auto ec_key = getEC_KEYfromEVP_PKEY(pkey);

    return key_pair_t(getPrivateKey(ec_key), getPublicKey(ec_key));
}

void Cryptography::freeEC_KEY(EC_KEY *ec_key) {

    EC_KEY_free(ec_key);
}

ec_key_t Cryptography::getEC_KEYfromEVP_PKEY(evp_pkey_t &pkey) const {

    auto *ec_key = EVP_PKEY_get1_EC_KEY(pkey.get());

    if (ec_key == nullptr) {
        throw CryptographyError("Unexpected error while extracting ECDH key pair, " + getOpenSSLError());
    }

    return ec_key_t(ec_key, &freeEC_KEY);
}

pub_key_t Cryptography::getPublicKey(ec_key_t &ec_key) const {

    std::array<unsigned char, PUB_KEY> pub_key{};
    auto bn_ctx = getBN_CTX();
    auto ec_group = getEC_GROUP(ec_key);
    auto ec_point = getEC_POINT(ec_key);

    if (EC_POINT_point2oct(ec_group, ec_point, POINT_CONVERSION_COMPRESSED, pub_key.data(), pub_key.size(), bn_ctx.get()) != PUB_KEY) {
        throw CryptographyError("Unexpected error while getting ECDH public key, " + getOpenSSLError());
    }

    return toByteArray(pub_key);
}

priv_key_t Cryptography::getPrivateKey(ec_key_t &ec_key) const {

    std::array<unsigned char, PRIV_KEY> priv_key{};
    auto bignum = getBIGNUM(ec_key);

    if (BN_bn2lebinpad(bignum, priv_key.data(), priv_key.size()) != PRIV_KEY) {
        throw CryptographyError("Unexpected error while getting ECDH private key, " + getOpenSSLError());
    }

    return toByteArray(priv_key);
}

void Cryptography::freeBN_CTX(BN_CTX *bn_ctx) {

    BN_CTX_free(bn_ctx);
}

bn_ctx_t Cryptography::getBN_CTX() const {

    auto bn_ctx = BN_CTX_secure_new();

    if (bn_ctx == nullptr) {
        throw CryptographyError("Unexpected error while creating BN_CTX, " + getOpenSSLError());
    }
    return bn_ctx_t(bn_ctx, &freeBN_CTX);
}

const EC_GROUP * Cryptography::getEC_GROUP(ec_key_t &ec_key) const {

    auto ec_group = EC_KEY_get0_group(ec_key.get());

    if (ec_group == nullptr) {
        throw CryptographyError("Unexpected error while getting EC_GROUP, " + getOpenSSLError());
    }

    return ec_group;
}

const EC_POINT * Cryptography::getEC_POINT(ec_key_t &ec_key) const {

    auto ec_point = EC_KEY_get0_public_key(ec_key.get());

    if (ec_point == nullptr) {
        throw CryptographyError("Unexpected error while getting EC_POINT, " + getOpenSSLError());
    }

    return ec_point;
}

const BIGNUM * Cryptography::getBIGNUM(ec_key_t &ec_key) const {

    auto bignum = EC_KEY_get0_private_key(ec_key.get());

    if (bignum == nullptr) {
        throw CryptographyError("Unexpected error while getting BIGNUM, " + getOpenSSLError());
    }

    return bignum;
}

signature_t Cryptography::createSignature(const priv_key_t &priv_key, const bytes_t &data) const {

    try {

        auto pkey = getEC_KEYFromPrivateKey(priv_key, NID_X9_62_prime256v1);

        return getSignature(data, pkey);

    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("HMAC signing: ") + e.what());
    }

}

signature_t Cryptography::getSignature(const bytes_t &data, const ec_key_t &pkey) const {

    auto sig_len = static_cast<unsigned int>(ECDSA_size(pkey.get()));

    std::vector<unsigned char> signature(sig_len);

    std::vector<unsigned char> digest = toUCharVector(data);

    if (ECDSA_sign(0, digest.data(), static_cast<int>(digest.size()), signature.data(), &sig_len, pkey.get()) != SUCCSESS) {
        throw CryptographyError("");
    }

    signature.resize(sig_len);

    return toBytes(signature);
}

bool Cryptography::isValidSignature(const pub_key_t &pub_key,
                                    const signature_t &signature,
                                    const bytes_t &data) const {

    try {

        auto pkey = getEC_KEYFromPublicKey(pub_key, NID_X9_62_prime256v1);

        auto dgst = toUCharVector(data);

        auto sign = toUCharVector(signature);

        return validateSignature(pkey, dgst, sign);

    }
    catch (CryptographyError &e) {
        throw CryptographyError(std::string("HMAC sign verification: ") + e.what());
    }
}

bool Cryptography::validateSignature(const ec_key_t &pkey,
                                     const std::vector<unsigned char> &dgst,
                                     const std::vector<unsigned char> &sign) const {

    auto ret =  ECDSA_verify(0, dgst.data(), static_cast<int>(dgst.size()), sign.data(), static_cast<int>(sign.size()), pkey.get());

    if (ret != VALID && ret != INVALID) {
        throw CryptographyError("Unexpected error while validating signature");
    }

    return ret == VALID;
}

bignum_t Cryptography::getBIGNUMFromPrivKey(const priv_key_t &priv_key) const {

    auto private_key = toUCharVector(priv_key);

    auto bignum = BN_lebin2bn(private_key.data(), static_cast<int>(private_key.size()), nullptr);

    if (bignum == nullptr) {
        throw CryptographyError("Unexpected error while creating BIGNUM from priv_key_t " + getOpenSSLError());
    }

    return bignum_t(bignum, &freeBIGNUM);
}

ec_key_t Cryptography::getEC_KEYFromBIGNUM(const bignum_t &bignum, int nid) const {

    auto ec_key = createEC_KEY(nid);

    if (EC_KEY_set_private_key(ec_key.get(), bignum.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while setting private key to EC_KEY, " + getOpenSSLError());
    }

    return ec_key;
}

ec_key_t Cryptography::createEC_KEY(int nid, point_conversion_form_t point_conversion_form) const {

    auto ec_key = EC_KEY_new_by_curve_name(nid);

    if (ec_key == nullptr) {
        throw CryptographyError("Unexpected error while creating EC_KEY" + getOpenSSLError());
    }

    EC_KEY_set_conv_form(ec_key, point_conversion_form);

    return ec_key_t(ec_key, &freeEC_KEY);
}

ec_key_t Cryptography::getEC_KEYFromPublicKey(const pub_key_t &pub_key, int nid) const {

    auto ec_key = createEC_KEY(nid);

    auto ec_point = getEC_POINTFromPublicKey(pub_key, nid);

    if (EC_KEY_set_public_key(ec_key.get(), ec_point.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while setting public key to EC_KEY, " + getOpenSSLError());
    }

    return ec_key;
}

void Cryptography::freeBIGNUM(BIGNUM *bignum) {

    BN_free(bignum);
}

void Cryptography::freeEC_POINT(EC_POINT *ec_point) {

    EC_POINT_free(ec_point);
}

void Cryptography::freeEC_GROUP(EC_GROUP *ec_group) {

    EC_GROUP_free(ec_group);
}

ec_group_t Cryptography::createEC_GROUP(int nid) const {

    auto ec_group =  EC_GROUP_new_by_curve_name(nid);

    if (ec_group == nullptr) {
        throw CryptographyError("Unexpected error while creating EC_GROUP, " + getOpenSSLError());
    }

    return ec_group_t(ec_group, &freeEC_GROUP);
}

ec_point_t Cryptography::createEC_POINT(const ec_group_t &ec_group) const {

    auto ec_point = EC_POINT_new(ec_group.get());

    if (ec_point == nullptr) {
        throw CryptographyError("Unexpected error while creating EC_POINT, " + getOpenSSLError());
    }

    return ec_point_t(ec_point, &freeEC_POINT);
}

bn_ctx_t Cryptography::createBN_CTX() const {

    auto bn_ctx = BN_CTX_new();

    if (bn_ctx == nullptr) {
        throw CryptographyError("Unexpected error while creating BN_CTX, " + getOpenSSLError());
    }

    return bn_ctx_t(bn_ctx, &freeBN_CTX);
}

ec_key_t Cryptography::getEC_KEYFromPrivateKey(const priv_key_t &priv_key, int nid) const {

    auto bignum = getBIGNUMFromPrivKey(priv_key);

    return getEC_KEYFromBIGNUM(bignum, nid);
}

ec_point_t Cryptography::getEC_POINTFromPublicKey(const pub_key_t &pub_key, int nid) const {

    auto ec_group = createEC_GROUP(nid);

    auto ec_point = createEC_POINT(ec_group);

    auto bn_ctx = createBN_CTX();

    if (EC_POINT_oct2point(ec_group.get(), ec_point.get(), toUCharVector(pub_key).data(), pub_key.size(), bn_ctx.get()) != SUCCSESS) {
        throw CryptographyError("Unexpected error while setting EC_POINT to EC_KEY, " + getOpenSSLError());
    }

    return ec_point;
}





















