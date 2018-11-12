//
// Created by Daniel Bigos on 11.11.18.
//

#include "Transaction.hpp"

using namespace chasm;
using namespace chasm::primitives;

bool Transaction::operator==(const Transaction &rh) const {
    return compare_list_of_ptrs(inputs_, rh.inputs_) &&
           compare_list_of_ptrs(outputs_, rh.outputs_);
}