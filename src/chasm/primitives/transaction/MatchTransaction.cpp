//
// Created by Daniel Bigos on 11.11.18.
//

#include "MatchTransaction.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

bool MatchTransaction::operator==(const MatchTransaction &rh) const {
    return compare_collection(offerHash_, rh.offerHash_) &&
           compare_collection(address_, rh.address_) &&
           confirmationFeeIdx_ == rh.confirmationFeeIdx_ &&
           bailIdx_ == rh.bailIdx_;
}
