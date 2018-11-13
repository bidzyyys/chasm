//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_CONFIRMATION_TRANSACTION_H
#define CHASM_CONFIRMATION_TRANSACTION_H

#include <chasm/serialization/Serializable.hpp>
#include <chasm/types.hpp>
#include <chasm/tokens/Token.hpp>

namespace chasm::primitives::transaction {
    class ConfirmationTransaction;
}

namespace boost::serialization {
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::ConfirmationTransaction &tx,
                   unsigned int version);
}

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

        bool operator==(const ConfirmationTransaction &rh) const;

    private:
        friend class boost::serialization::access;

        template <typename Archive>
        friend void boost::serialization::serialize(Archive &ar, ConfirmationTransaction &tx,
                       unsigned int version);


        hash_t offerHash_; //!< Exchange to be confirmed

        uptr_t<proof_t> proofTokenIn_; //!< Proof of tx inclusion (seller's transaction)
        uptr_t<proof_t> proofTokenOut_; //!< Proof of tx inclusion (buyer's transaction)

    };
}

namespace boost::serialization {
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::ConfirmationTransaction &tx,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(tx);
        ar & tx.offerHash_;
        ar & tx.proofTokenOut_;
        ar & tx.proofTokenOut_;
    }
}

#endif //CHASM_CONFIRMATION_TRANSACTION_H
