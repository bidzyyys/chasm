//
// Created by Daniel Bigos on 11.11.18.
//

#include "chasm/primitives/transaction/Input.hpp"

using namespace chasm::primitives::transaction;

bool Input::operator==(const Input &rh) const {
    return utxo_ == rh.utxo_;
}
