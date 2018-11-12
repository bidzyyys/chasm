//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_TOKENS_HPP
#define CHASM_TOKENS_HPP

#include <cstdint>

namespace chasm::common{

    enum class Token : uint16_t {
        Bitcoin,
        Ethereum,
        Litecoin,
        OMG
    };

}


#endif //CHASM_TOKENS_HPP
