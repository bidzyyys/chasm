//
// Created by Daniel Bigos on 11.11.18.
//

#include "Header.hpp"

using namespace chasm;
using namespace chasm::primitives;


bool Header::operator==(const Header &rh) const {
    return compare_collection(prevTxHash_, rh.prevTxHash_) &&
           compare_collection(merkleTreeRoot_, rh.merkleTreeRoot_) &&
           timestamp_ == rh.timestamp_ &&
           nonce_ == rh.nonce_ &&
           difficulty_ == rh.difficulty_;
}
