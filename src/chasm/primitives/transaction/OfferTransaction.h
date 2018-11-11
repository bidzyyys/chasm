//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_OFFER_TRANSACTION_H
#define CHASM_OFFER_TRANSACTION_H

#include <chasm/primitives/Transaction.h>
#include <chasm/common/tokens.hpp>


namespace chasm::primitives::transaction {

    struct OfferTransaction: public Transaction {

        common::token_t tokenIn;
        common::types::value_t valueIn;

        common::token_t tokenOut;
        common::types::value_t valueOut;

        common::types::address_t

        common::types::timestamp_t timeout;

    };

}

#endif //CHASM_OFFER_TRANSACTION_H
