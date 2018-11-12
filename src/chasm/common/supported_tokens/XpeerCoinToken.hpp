//
// Created by Piotr Żelazko on 12/11/2018.
//

#ifndef CHASM_XPEERCOINTOKEN_HPP
#define CHASM_XPEERCOINTOKEN_HPP

#include "Token.hpp"

namespace chasm::common::tokens {
    class XpeerCoinToken : public Token {
    public:
        std::unique_ptr<TransactionInclusionProof> buildProof(const std::vector<std::byte> &vector) const override;


        ~XpeerCoinToken() override = default;

    };
}


#endif //CHASM_XPEERCOINTOKEN_HPP
