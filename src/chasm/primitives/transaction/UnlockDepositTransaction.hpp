//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
#define CHASM_UNLOCK_DEPOSIT_TRANSACTION_H

#include <vector>
#include <chasm/primitives/Transaction.hpp>
#include <chasm/tokens/Token.hpp>

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
    public:
        enum class TransactionSide : uint8_t {
            seller,
            buyer
        };

        ~UnlockDepositTransaction() override = default;

        bool operator==(const UnlockDepositTransaction &rh) const;

    private:

        hash_t offerHash_; //!< Exchange id
        TransactionSide side_; //!< Either seller or buyer. This side of the exchange will be checked
        uptr_t<proof_t> proof_; //!< Proof of tx inclusion
        out_idx_t bailIndex_; //!< Index of bail (in outputs)
    };
}

#endif //CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
