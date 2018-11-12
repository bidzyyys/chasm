//
// Created by Daniel Bigos on 11.11.18.
//

#include "UnlockDepositTransaction.hpp"

using namespace chasm::primitives::transaction;
using namespace chasm::common::types;

bool UnlockDepositTransaction::operator==(const UnlockDepositTransaction &rh) const {
    return compare_collection(offerHash_, rh.offerHash_) &&
            token_ == rh.token_ &&
//           compare_collection(proof_, rh.proof_) &&
           bailIndex_ == rh.bailIndex_;
}
