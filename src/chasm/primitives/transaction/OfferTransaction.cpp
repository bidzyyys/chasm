//
// Created by Daniel Bigos on 11.11.18.
//

#include "OfferTransaction.hpp"

using namespace chasm::primitives::transaction;
using namespace chasm::common::types;

bool OfferTransaction::operator==(const OfferTransaction &rh) const {
    return tokenIn_ == rh.tokenIn_ &&
            valueIn_ == rh.valueIn_ &&
            tokenOut_ == rh.tokenOut_ &&
            valueOut_ == rh.valueOut_ &&
            compare_collection(address_, rh.address_) &&
            offerTimeout_ == rh.offerTimeout_ &&
            nonce_ == rh.nonce_ &&
            confirmationFeeIndex_ == rh.confirmationFeeIndex_ &&
            bailIndex_ == rh.bailIndex_;
}
