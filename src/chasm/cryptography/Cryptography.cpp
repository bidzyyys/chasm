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
        evp_t evp = initEVP(EVP_sha256());

        std::array<unsigned char, HASH256> output_c{};

        updateEVP(evp, data);

        if(finishEVP(evp, output_c) != HASH256) {
            throw CryptographyError("Unexpected length of hash");
        }

        return toByteArray(output_c);
    }
    catch(CryptographyError &e) {
        throw CryptographyError(std::string("Cryptography: ") + e.what());
    }
}

evp_t Cryptography::newEVP() const {
    auto evp = EVP_MD_CTX_new();
    if(evp == nullptr) {
        throw CryptographyError("Unexpected error while creating EVP, " + getOpenSSLError());
    }
    return evp_t(evp, &freeEVP);
}

void Cryptography::freeEVP(EVP_MD_CTX *evp) {
    EVP_MD_CTX_free(evp);
}

evp_t Cryptography::initEVP(const EVP_MD *evp_md, ENGINE *engine) const {

    auto evp = newEVP();

    if (EVP_DigestInit_ex(evp.get(), evp_md, engine) == 0) {
        throw CryptographyError("Unexpected error while initializing EVP, " + getOpenSSLError());
    }

    return evp;
}

const std::string Cryptography::getOpenSSLError() const {
    return "error code: " + std::to_string(ERR_get_error());
}






