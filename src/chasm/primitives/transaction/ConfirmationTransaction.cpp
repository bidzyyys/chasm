//
// Created by Daniel Bigos on 11.11.18.
//

#include "ConfirmationTransaction.hpp"

using namespace chasm::primitives::transaction;

bool ConfirmationTransaction::operator==(const ConfirmationTransaction &rh) const {
    return compare_collection(offerHash_, rh.offerHash_) &&
            proofTokenIn_ == rh.proofTokenIn_ &&
            proofTokenOut_ == rh.proofTokenOut_;
}
