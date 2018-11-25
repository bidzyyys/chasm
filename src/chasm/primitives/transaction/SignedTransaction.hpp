//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_SIGNED_TRANSACTION_HPP
#define CHASM_SIGNED_TRANSACTION_HPP

#include <chasm/primitives/Transaction.hpp>

namespace chasm::primitives::transaction {

    /*!
     * \brief A transaction with signatures
     *
     * Each input that requires a signature must be signed (whole transaction must be signed)
     * and the signatures must be added at the end.
     *
     * Signatures do not sign themselves - it is stupid.
     * The order of the signatures must be the same as the order of the corresponding inputs.
     * If an input does not require a signature, omit this signature and continue with the next required.
     *
     */
    class SignedTransaction {
    public:
        virtual ~SignedTransaction() = default;

    private:
        std::unique_ptr<Transaction> transaction_;

        std::list<uptr_t<signature_t>> signatures_;
    };

}

#endif //CHASM_SIGNED_TRANSACTION_HPP
