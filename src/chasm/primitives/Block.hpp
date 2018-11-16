//
// Created by Piotr Żelazko on 02/11/2018.
//

#ifndef CHASM_BLOCK_H
#define CHASM_BLOCK_H

#include <cstddef>
#include <array>
#include <list>
#include <chasm/serialization/traits.hpp>

#include "chasm/primitives/transaction/SignedTransaction.hpp"
#include "chasm/types.hpp"

namespace chasm::primitives {

    /*!
     * \brief Set of transactions (aka. Block)
     *
     */
    class Block {
    public:


        //! \brief adjusts nonce by adding 1 to the current value
//        void adjustNonce();

        //! \brief sets the timestamp field to the current timestamp
//        void adjustTimestamp();

        /*! \brief adds the transaction to the block
         *
         *  \b NOTE: this does not check the requirement whether, the block fulfills the 1MB limitation
         */
//        void addTransaction(std::unique_ptr<Transaction> tx);


        /*! \brief adds a transaction and checks size limitation
         *
         * \arg tx - a transaction to be added
         * \returns either empty optional in case the \a tx was added or given tx when it was impossible to add the \a tx
         */
//        std::optional<std::unique_ptr<Transaction>> tryAddTransaction(std::unique_ptr<Transaction> tx);

        hash_t const &getPrevTxHash() const;

        hash_t const &getMerkleTreeRoot() const;

        timestamp_t getTimestamp() const;

        nonce_t getNonce() const;

        difficulty_t getDifficulty() const;

        bool operator==(const Block &rh) const;

        virtual ~Block() = default;

        using class_id_e = serialization::traits::classes::class_id;
        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Block>;

        using inheritance_t = serialization::traits::inheritance::is_root_t;


    private:

        /*!
         * \brief Represents Block's header
         *
         * \b Note: Hash of the block is a hash of the header.
         */
        struct Header {
            hash_t prevTxHash_; //!< Pointer to the previous block

            hash_t merkleTreeRoot_; //!< Merkle tree root of a tree made of included transactions

            // TODO: must be higher than the timestamp of the previous block
            timestamp_t timestamp_; //!< Timestamp of the current block

            nonce_t nonce_; //!< Adjustable value. Used when mining new blocks

            difficulty_t difficulty_; //!< Number of leading bits of hash that must be zeroed
        };

        using signed_tx_t = chasm::primitives::transaction::SignedTransaction;

        Header header_;

        std::list<uptr_t<signed_tx_t>> transactions_; //<! List of transactions included in the block

    };
}

#endif //CHASM_BLOCK_H
