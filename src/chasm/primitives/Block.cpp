//
// Created by Daniel Bigos on 11.11.18.
//

#include <ctime>
#include "Block.hpp"

using namespace chasm;
using namespace chasm::primitives;

bool Block::operator==(const Block &rh) const {
//    return header_ == rh.header_ &&
//            compare_list_of_ptrs(transactions_, rh.transactions_);
    return true;
}

hash_t const &Block::getPrevTxHash() const {
    return header_.prevBlockHash;
}

hash_t const &Block::getMerkleTreeRoot() const {
    return header_.merkleTreeRoot_;
}

timestamp_t Block::getTimestamp() const {
    return header_.timestamp_;
}

nonce_t Block::getNonce() const {
    return header_.nonce_;
}

difficulty_t Block::getDifficulty() const {
    return header_.difficulty_;
}


Block::Block(chasm::hash_t prevBlock) {
    header_.prevBlockHash = prevBlock;
    header_.timestamp_ = static_cast<timestamp_t>(std::time(nullptr));
    header_.nonce_ = 0;
    header_.difficulty_ = 0;
}

Block::Block(hash_t prevBlock, hash_t merkleTreeRoot, timestamp_t timestamp, nonce_t nonce, difficulty_t difficulty)
        : header_{prevBlock, merkleTreeRoot, timestamp, nonce, difficulty} {}
