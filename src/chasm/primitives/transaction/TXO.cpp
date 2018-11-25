//
// Created by Daniel Bigos on 11.11.18.
//

#include "TXO.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

TXO::TXO(const hash_t &txHash, out_idx_t index) : txHash_(txHash), index_(index) {}

TXO::TXO(hash_t &&txHash, out_idx_t index) : txHash_(txHash), index_(index) {}

bool TXO::operator==(const TXO &rh) const {
    return compare_collection(txHash_, rh.txHash_) &&
           index_ == rh.index_;
}

const hash_t &TXO::getTxHash() const {
    return txHash_;
}

out_idx_t TXO::getIndex() const {
    return index_;
}

