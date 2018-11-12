//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_OUTPUT_H
#define CHASM_OUTPUT_H

#include <chasm/types.hpp>
#include <chasm/primitives/Serializable.hpp>

namespace chasm::primitives::transaction {
    class Output;

    class SimpleOutput;

    class FreeOutput;
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::Output &output,
                   unsigned int version);

    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::SimpleOutput &output,
                   unsigned int version);

    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::FreeOutput &output,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Base class for all kinds of outputs. Abstract.
     */
    class Output : public Serializable {
    public:
        ~Output() override = 0;

        bool operator==(const Output &rh) const;

    protected:
        types::value_t value_;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Output &output,
                                                    unsigned int version);
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
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, SimpleOutput &output,
                                                    unsigned int version);

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
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, FeeOutput &output,
                                                    unsigned int version);

        types::hash_t offerHash_;
    };

}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::Output &output,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(output);
        ar & output.value_;
    }

    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::SimpleOutput &output,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::transaction::Output>(output);
        ar & output.receiver_;
    }

    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::FeeOutput &output,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::transaction::Output>(output);
        ar & output.offerHash_;
    }
}

BOOST_SERIALIZATION_ASSUME_ABSTRACT(chasm::primitives::transaction::Output)

#endif //CHASM_OUTPUT_H
