//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TYPES_H
#define CHASM_TYPES_H


#include <cstddef>
#include <array>

namespace chasm::common::types {

    using hash_t = std::array<std::byte, 32>;

    using pub_key_t = std::array<std::byte, 33>;
    using priv_key_t = std::array<std::byte, 32>;

    using signature_t = std::array<std::byte, 72>;
    using address_t = pub_key_t;

    using value_t = uint64_t;

    using out_idx_t = uint16_t; // A transaction cannot have more outputs, as there is block size limitation
    using in_idx_t = out_idx_t;
}


#endif //CHASM_TYPES_H
