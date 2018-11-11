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
    class Output : public Serializable {
    public:
        ~Output() override = 0;
    };

    /*!
     * \brief Simple output should be used to make a simple transfer.
     *
     * To unlock this output, the spender must sign the transaction with the private key corresponding to the address.
     */
    class SimpleOutput : public Output {
    public:
        ~SimpleOutput() override = default;

    private:
        common::types::address_t receiver_;
        common::types::value_t value_;
    };


    /*!
     * \brief Fee output should be used as an output of either an offer or a match.
     *
     * This kind of an output can be spend in two cases:
     *  - as an input to the confirmation tx (hashes of the offers must be equal)
     *  - as an input to the deposit unlock tx
     */
    class FeeOutput : public Output {
    public:

        ~FeeOutput() override = default;

    private:
        common::types::hash_t offerHash_;
        common::types::value_t value_;

    };

}

#endif //CHASM_OUTPUT_H


//FIXME: change headers into .hpp