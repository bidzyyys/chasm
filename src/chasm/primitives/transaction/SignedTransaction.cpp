//
// Created by Daniel Bigos on 12.11.18.
//

#include "SignedTransaction.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

bool SignedTransaction::operator==(const SignedTransaction &rh) const {
// TODO comparators
    return *transaction_ == *rh.transaction_ &&
           compare_list_of_ptrs(signatures_, rh.signatures_);
}