//
// Created by Piotr Żelazko on 02/11/2018.
//

#ifndef CHASM_BLOCK_H
#define CHASM_BLOCK_H

#include <cstddef>
#include <array>
#include <list>

#include "chasm/primitives/transaction/SignedTransaction.hpp"
#include "chasm/types.hpp"
#include "Serializable.hpp"
#include "Header.hpp"

namespace chasm::primitives {

    /*!
     * \brief Set of transactions (aka. Block)
     *
     */
    class Block : public Serializable {
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
//        boost::optional<std::unique_ptr<Transaction>> tryAddTransaction(std::unique_ptr<Transaction> tx);

        ~Block() override = default;

    private:
        using signed_tx_t = chasm::primitives::transaction::SignedTransaction;
        
        Header header_;
//        std::list<uptr_t<signed_tx_t>> transactions_; //<! List of transactions included in the block

    };
}


#endif //CHASM_BLOCK_H
