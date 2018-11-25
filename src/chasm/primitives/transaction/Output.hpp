//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_OUTPUT_H
#define CHASM_OUTPUT_H

#include <chasm/types.hpp>
#include <chasm/serialization/traits.hpp>

namespace chasm::primitives::transaction {

    /*!
     * \brief Base class for all kinds of outputs. Abstract.
     */
    class Output {
    public:
        explicit Output(value_t value);

        value_t getValue() const;

        virtual ~Output() = 0;

        using class_id_e = serialization::traits::classes::class_id;
        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Output>;

        using inheritance_t = serialization::traits::inheritance::is_root_t;

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
        SimpleOutput(value_t value, const address_t &receiver);

        const address_t &getReceiver() const;

        ~SimpleOutput() override = default;

        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::SimpleOutput>;
        using inheritance_t = serialization::traits::inheritance::is_derived_t<Output>;
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

        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::FeeOutput>;
        using inheritance_t = serialization::traits::inheritance::is_derived_t<Output>;
    private:
        types::hash_t offerHash_;
    };

}
#endif //CHASM_OUTPUT_H
