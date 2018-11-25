//
// Created by Daniel Bigos on 11.11.18.
//

#include "chasm/primitives/transaction/Input.hpp"

using namespace chasm::primitives::transaction;

bool Input::operator==(const Input &rh) const {
    return utxo_ == rh.utxo_;
}

const TXO &Input::getUTXO() const {
    return utxo_;
}

Input::Input(hash_t&& hash, in_idx_t index): utxo_(hash, index)
{}

Input::Input(hash_t const& hash, in_idx_t index): utxo_(hash, index)
{}



