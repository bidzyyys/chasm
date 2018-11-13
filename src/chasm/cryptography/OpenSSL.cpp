//
// Created by Daniel Bigos on 13.11.18.
//

#include <iostream>
#include <memory>
#include "OpenSSL.hpp"

using namespace chasm::cryptography;

hash256_t OpenSSL::test() {
    char tab[3] = {'a','b', 'c'};

    unsigned char res[HASH256];

    auto hmac = HMAC_CTX_new();
    HMAC_Init_ex(hmac, tab, 3, EVP_sha256(), nullptr);

    if(HMAC_Update(hmac, res, HASH256))
        std::cout<<"Update success"<<std::endl;

    unsigned int len = 0;
    if(HMAC_Final(hmac, res, &len))
        std::cout<<"Final success"<<std::endl;
    HMAC_CTX_free(hmac);

    return hash256_t();
}
