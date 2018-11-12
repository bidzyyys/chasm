//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TYPES_H
#define CHASM_TYPES_H


#include <cstddef>
#include <array>
#include <list>
#include "chasm/common/supported_tokens/Token.hpp"

namespace chasm::common::types {

    using hash_t = std::array<std::byte, 32>;

    using pub_key_t = std::array<std::byte, 33>;
    using priv_key_t = std::array<std::byte, 32>;

    using signature_t = std::array<std::byte, 72>;
    using address_t = pub_key_t;

    using value_t = uint64_t;

    using nonce_t = uint64_t;
    using difficulty_t = uint8_t;

    using out_idx_t = uint16_t; // A transaction cannot have more outputs, as there is block size limitation
    using in_idx_t = out_idx_t;

    using token_t = chasm::common::tokens::Token::Tokens;
    using proof_t = chasm::common::tokens::Token::TransactionInclusionProof;

    using timestamp_t = uint64_t;

    template <typename T>
    bool compare_collection(const T &l, const T &r){
        return std::equal(l.cbegin(), l.cend(), r.cbegin());
    }

    template <typename T>
    bool compare_list_of_ptrs(const std::list<T> &l, const std::list<T> &r){
        return std::equal(l.cbegin(), l.cend(), r.cbegin(), [](const T &l_ptr, const T &r_ptr){
            return *l_ptr == *r_ptr;
        });
    }
}


#endif //CHASM_TYPES_H
