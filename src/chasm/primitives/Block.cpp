//
// Created by Daniel Bigos on 11.11.18.
//

#include "Block.hpp"

using namespace chasm::primitives;


bool Block::operator==(const Block &rh) const {
    return header_ == rh.header_ &&
            compare_list_of_ptrs(transactions_, rh.transactions_);
}
