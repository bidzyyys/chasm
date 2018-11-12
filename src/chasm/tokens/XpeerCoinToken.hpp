//
// Created by Piotr Żelazko on 12/11/2018.
//

#ifndef CHASM_XPEERCOINTOKEN_HPP
#define CHASM_XPEERCOINTOKEN_HPP

#include "Token.hpp"

namespace chasm::tokens {
    class XpeerCoinToken : public Token {
    public:
        boost::optional<uptr_t<TransactionInclusionProof>> buildProof(bytes_t const& vector) const override;

        ~XpeerCoinToken() override = default;

        boost::optional<uptr_t<chasm::tokens::Token::Address>> buildAddress(types::bytes_t const &bytes) const override;

    };
}


#endif //CHASM_XPEERCOINTOKEN_HPP
