//
// Created by Piotr Żelazko on 12/11/2018.
//

#include "XpeerCoinToken.hpp"

using namespace chasm;
using namespace chasm::tokens;

boost::optional<uptr_t<Token::TransactionInclusionProof>>
XpeerCoinToken::buildProof(const std::vector<std::byte> &vector) const {
    return std::unique_ptr<TransactionInclusionProof>();
}

boost::optional<uptr_t<chasm::tokens::Token::Address>> XpeerCoinToken::buildAddress(types::bytes_t const &bytes) const {
    return boost::optional<uptr_t<chasm::tokens::Token::Address>>();
}


