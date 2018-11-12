//
// Created by Daniel Bigos on 11.11.18.
//

#include "MiningTransaction.hpp"

using namespace chasm::primitives::transaction;

bool MiningTransaction::operator==(const MiningTransaction &rh) const {
    return Transaction::operator==(rh);
}
