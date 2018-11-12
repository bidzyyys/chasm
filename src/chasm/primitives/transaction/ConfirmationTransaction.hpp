//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_CONFIRMATION_TRANSACTION_H
#define CHASM_CONFIRMATION_TRANSACTION_H

#include <chasm/primitives/Serializable.hpp>
#include <chasm/types.hpp>
#include <chasm/tokens/Token.hpp>

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction of type confirmation
     *
     * This transaction can be send by anyone who knows the proofs of inclusion of both sides of the exchange on the
     * corresponding chains.
     * Inputs to this transaction can be of type FeeOutput, but only those referencing the exchange to be confirmed
     */
    class ConfirmationTransaction : public Serializable {
    public:

        ~ConfirmationTransaction() override = default;

    private:

        types::hash_t offerHash_;

        uptr_t<types::proof_t> proofTokenIn_;
        uptr_t<types::proof_t> proofTokenOut_;

    };
}

#endif //CHASM_CONFIRMATION_TRANSACTION_H
