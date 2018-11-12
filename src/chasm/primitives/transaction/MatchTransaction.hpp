//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_MATCH_TRANSACTION_H
#define CHASM_MATCH_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>

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

    private:

        common::types::hash_t offerHash_; //!< Hash of the accepted offer
        common::types::address_t address_; //!< Receiver's address (on the blockchain where the exchange happens)

        common::types::out_idx_t confirmationFeeIdx_; //!< Index of confirmation fee. The output must be of type \b FeeOutput
        common::types::out_idx_t bailIdx_; //!< Index of a bail.

    };
}

#endif //CHASM_MATCH_TRANSACTION_H