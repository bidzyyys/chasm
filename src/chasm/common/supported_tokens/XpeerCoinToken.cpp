//
// Created by Piotr Żelazko on 12/11/2018.
//

#include "XpeerCoinToken.hpp"

using namespace chasm::common::tokens;

std::unique_ptr<Token::TransactionInclusionProof>
XpeerCoinToken::buildProof(const std::vector<std::byte> &vector) const {
    return std::unique_ptr<TransactionInclusionProof>();
}


