//
// Created by Daniel Bigos on 11.11.18.
//

#ifndef CHASM_HEADER_H
#define CHASM_HEADER_H

#include <chasm/types.hpp>

namespace chasm::primitives {

    /*!
     * \brief Represents Block's header
     *
     * \b Note: Hash of the block is a hash of the header.
     */
    class Header {
    public:
//        ~Header() override = default;

        bool operator==(const Header &rh) const;

    private:

        hash_t prevTxHash_; //!< Pointer to the previous block

        hash_t merkleTreeRoot_; //!< Merkle tree root of a tree made of included transactions

        // TODO: must be higher than the timestamp of the previous block
        timestamp_t timestamp_; //!< Timestamp of the current block

        nonce_t nonce_; //!< Adjustable value. Used when mining new blocks

        difficulty_t difficulty_; //!< Number of leading bits of hash that must be zeroed
    };
}

#endif //CHASM_HEADER_H
