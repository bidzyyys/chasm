//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_MATCH_TRANSACTION_H
#define CHASM_MATCH_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>

namespace chasm::primitives::transaction {
    class MatchTransaction;
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::MatchTransaction &tx,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Offer match transaction type
     *
     * This class represents a transaction of a type of a match.
     * This kind of a transaction should be send whenever a user wants to accept an broadcast offer.
     */
    class MatchTransaction : public Transaction {
    public:

        ~MatchTransaction() override = default;

        bool operator==(const MatchTransaction &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, MatchTransaction &tx,
                                                    unsigned int version);

        hash_t offerHash_; //!< Hash of the accepted offer

        address_t address_; //!< Receiver's address (on the blockchain where the exchange happens)

        out_idx_t confirmationFeeIdx_; //!< Index of confirmation fee. The output must be of type \b FeeOutput

        out_idx_t bailIdx_; //!< Index of bail.

    };
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::MatchTransaction &tx,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Transaction>(tx);
        ar & tx.offerHash_;
        ar & tx.address_;
        ar & tx.confirmationFeeIdx_;
        ar & tx.bailIdx_;
    }
}


#endif //CHASM_MATCH_TRANSACTION_H
