//
// Created by Piotr Żelazko on 02/11/2018.
//

#ifndef CHASM_BLOCK_H
#define CHASM_BLOCK_H

#include <cstddef>
#include <array>
#include <list>

#include "chasm/common/types.h"
#include "Transaction.h"

namespace chasm::primitives{
    class Block {
    public:

    private:
        struct Header{
            common::types::hash_t prev_tx_hash;
            common::types::hash_t merkle_tree_root;
            uint64_t timestamp;
            uint64_t  nonce;
            uint8_t difficulty;
        };
        Header header_;
        std::list<Transaction> transactions_;
    };
}



#endif //CHASM_BLOCK_H
