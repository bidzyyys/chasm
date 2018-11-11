//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_OFFER_TRANSACTION_H
#define CHASM_OFFER_TRANSACTION_H

#include <chasm/primitives/Transaction.h>
#include <chasm/common/tokens.hpp>


namespace chasm::primitives::transaction {


    class OfferTransaction : public Transaction {
    public:

        ~OfferTransaction() override = default;

    private:

        common::types::token_t tokenIn_; //!< Token being offered
        common::types::value_t valueIn_; //!< Value being offered

        common::types::token_t tokenOut_; //!< Token being demanded
        common::types::value_t valueOut_; //!< Value being demanded

        common::types::address_t address_; //!< Receiver's address (on the blockchain where the exchange happens)

        //! Time in seconds how long will the offer be 'matchable',
        //! starting from the timestamp of the block in which the transaction was included in.
        common::types::timestamp_t offerTimeout_;

        common::types::out_idx_t confirmationFeeIndex_; //!< Index of confirmation fee. The output must be of type \b FeeOutput
        common::types::out_idx_t bailIndex_; //!< Index of bail
    };

}

#endif //CHASM_OFFER_TRANSACTION_H
