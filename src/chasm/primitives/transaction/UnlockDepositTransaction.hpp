//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
#define CHASM_UNLOCK_DEPOSIT_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>
#include <vector>

namespace chasm::primitives::transaction{
    class UnlockDepositTransaction;
}

namespace boost::serialization{
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::UnlockDepositTransaction &tx,
                    unsigned int version);
}

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
        ~UnlockDepositTransaction() override = default;

        bool operator==(const UnlockDepositTransaction &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, UnlockDepositTransaction &tx,
                       unsigned int version);

        using proof_t = std::vector<std::byte>;

        common::types::hash_t offerHash_;
        common::types::token_t token_;
        proof_t proof_;

        common::types::out_idx_t bailIndex_;
    };
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::UnlockDepositTransaction &tx,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Transaction>(tx);
        ar & tx.offerHash_;
        ar & tx.token_;
        ar & tx.proof_;
        ar & tx.bailIndex_;
    }
}

#endif //CHASM_UNLOCK_DEPOSIT_TRANSACTION_H
