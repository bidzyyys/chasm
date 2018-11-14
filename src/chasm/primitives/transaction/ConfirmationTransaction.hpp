//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_CONFIRMATION_TRANSACTION_H
#define CHASM_CONFIRMATION_TRANSACTION_H

#include <chasm/types.hpp>
#include <chasm/tokens/Token.hpp>
#include <chasm/primitives/Transaction.hpp>

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction of type confirmation
     *
     * This transaction can be send by anyone who knows the proofs of inclusion of both sides of the exchange on the
     * corresponding chains.
     * Inputs to this transaction can be of type FeeOutput, but only those referencing the exchange to be confirmed
     */
    class ConfirmationTransaction : public Transaction {
    public:
        ~ConfirmationTransaction() override = default;

        bool operator==(const ConfirmationTransaction &rh) const;

    private:

        hash_t offerHash_; //!< Exchange to be confirmed

        uptr_t<proof_t> proofTokenIn_; //!< Proof of tx inclusion (seller's transaction)
        uptr_t<proof_t> proofTokenOut_; //!< Proof of tx inclusion (buyer's transaction)

    };
}

#endif //CHASM_CONFIRMATION_TRANSACTION_H
