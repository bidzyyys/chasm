//
// Created by Daniel Bigos on 11.11.18.
//

#include "TXO.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

bool TXO::operator==(const TXO &rh) const {
    return compare_collection(txHash_, rh.txHash_) &&
           index_ == rh.index_;
}

