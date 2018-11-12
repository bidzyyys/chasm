//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
#define CHASM_UNLOCK_DEPOSIT_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>
#include <vector>

namespace chasm::primitives::transaction {

    /*! \class UnlockDepositTransaction
     *  \brief Type of a transaction which enables a deposit unlock in case of unsuccessful transaction.
     *
     *  This transaction makes possible to unlock a deposit.
     *  The deposit can be unlocked if and only if the user has been honest and did make his part of the exchange
     *  and the deposit has not been unlocked.
     *  Note that this transaction is used to unlock both, the bail and the confirmation fee.
     *  This type of a transaction is also send in when an offer has not been accepted
     *  and the confirmation fee should unlocked.
     */
    class UnlockDepositTransaction : public Transaction {

    private:
        using proof_t = std::vector<std::byte>;

        common::types::hash_t offerHash_;
        common::types::token_t token_;
        proof_t proof_;

        common::types::out_idx_t bailIndex_;
    };
}

#endif //CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
