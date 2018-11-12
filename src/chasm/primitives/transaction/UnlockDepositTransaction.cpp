//
// Created by Daniel Bigos on 11.11.18.
//

#include "UnlockDepositTransaction.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

bool UnlockDepositTransaction::operator==(const UnlockDepositTransaction &rh) const {
    return Transaction::operator==(rh) &&
            compare_collection(offerHash_, rh.offerHash_) &&
            token_ == rh.token_ &&
            proof_ ==  rh.proof_ &&
            bailIndex_ == rh.bailIndex_;
}
