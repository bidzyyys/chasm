//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_OUTPUT_H
#define CHASM_OUTPUT_H

#include <chasm/common/types.h>
#include <chasm/primitives/Serializable.h>

namespace chasm::primitives::transaction {

    /*!
     * \brief Base class for all kinds of outputs. Abstract.
     */
    struct Output : public DTO {
        ~Output() override = 0;
    };

    /*!
     * \brief Simple output should be used to make a simple transfer.
     *
     * To unlock this output, the spender must sign the transaction with the private key corresponding to the address.
     */
    struct SimpleOutput : public Output {

        std::any acceptSerializator() override;

        ~SimpleOutput() override = default;

        common::types::address_t receiver;
        common::types::value_t value;
    };


    /*!
     * \brief Fee output should be used as an output of either an offer or a match.
     *
     * This kind of an output can be spend in two cases:
     *  - as an input to the confirmation tx (hashes of the offers must be equal)
     *  - as an input to the deposit unlock tx
     */
    struct FeeOutput : public Output {

        std::any acceptSerializator() override;

        ~FeeOutput() override = default;

        common::types::hash_t offer_hash;
        common::types::value_t value;

    };

}

#endif //CHASM_OUTPUT_H


//FIXME: change headers into .hpp