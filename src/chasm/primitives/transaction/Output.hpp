//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_OUTPUT_H
#define CHASM_OUTPUT_H

#include <chasm/types.hpp>

namespace chasm::primitives::transaction {

    /*!
     * \brief Base class for all kinds of outputs. Abstract.
     */
    class Output {
    public:
        virtual ~Output() = 0;

        bool operator==(const Output &rh) const;

    protected:
        types::value_t value_;
    };

    /*!
     * \brief Simple output should be used to make a simple transfer.
     *
     * To unlock this output, the spender must sign the transaction with the private key corresponding to the address.
     */
    class SimpleOutput : public Output {
    public:
        ~SimpleOutput() override = default;

        bool operator==(const SimpleOutput &rh) const;

    private:
        types::address_t receiver_;
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

        bool operator==(const FeeOutput &rh) const;

    private:
        types::hash_t offerHash_;
    };

}
#endif //CHASM_OUTPUT_H
