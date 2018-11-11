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
#include "Serializable.h"

namespace chasm::primitives {
    class Block : public Serializable {
    public:

        //TODO: move to the class that will be a wrapper of Block structure

        //! \brief adjusts nonce by adding 1 to the current value
        void adjustNonce();

        //! \brief sets the timestamp field to the current timestamp
        void adjustTimestamp();

        /*! \brief adds the transaction to the block
         *
         *  \b NOTE: this does not check the requirement whether, the block fulfills the 1MB limitation
         */
         void addTransaction(std::unique_ptr<Transaction> tx);


        /*! \brief adds a transaction and checks size limitation
         *
         * \arg tx - a transaction to be added
         * \returns either empty optional in case the \a tx was added or given tx when it was impossible to add the \a tx
         */
        boost::optional<std::unique_ptr<Transaction>> tryAddTransaction(std::unique_ptr<Transaction> tx);

        ~Block() override = default;

    private:
        using nonce_t = uint64_t;
        using difficulty_t = uint8_t;

        struct Header {
            common::types::hash_t prev_tx_hash;
            common::types::hash_t merkle_tree_root;
            uint64_t timestamp; // TODO: must be higher than the timestamp of the previous block
            nonce_t nonce;
            difficulty_t difficulty;
        };

        Header header_;
        std::list<std::unique_ptr<Transaction>> transactions_;

    };
}


#endif //CHASM_BLOCK_H


