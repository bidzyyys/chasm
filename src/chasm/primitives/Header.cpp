//
// Created by Daniel Bigos on 11.11.18.
//

#include "Header.h"

using namespace chasm::primitives;

bool Header::operator==(const Header &rh) const {
    return prev_tx_hash_ == rh.prev_tx_hash_ &&
            merkle_tree_root_ == rh.merkle_tree_root_ &&
            timestamp_ == rh.timestamp_ &&
            nonce_ == rh.nonce_ &&
            difficulty_ == rh.difficulty_;
}
