//
// Created by Daniel Bigos on 11.11.18.
//

#include "Header.hpp"

using namespace chasm::primitives;
using namespace chasm::common::types;

bool Header::operator==(const Header &rh) const {
    return  compare_collection(prev_tx_hash_, rh.prev_tx_hash_) &&
            compare_collection(merkle_tree_root_, rh.merkle_tree_root_) &&
            timestamp_ == rh.timestamp_ &&
            nonce_ == rh.nonce_ &&
            difficulty_ == rh.difficulty_;
}
