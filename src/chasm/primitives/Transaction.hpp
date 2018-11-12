//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TRANSACTION_H
#define CHASM_TRANSACTION_H

#include <list>
#include <chasm/primitives/transaction/Output.hpp>
#include "chasm/primitives/transaction/Input.hpp"
#include "chasm/primitives/Serializable.hpp"

namespace chasm::primitives {
    class Transaction;
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::Transaction &tx,
                   unsigned int version);
}

namespace chasm::primitives {

    /*!
     * \brief Basic transaction
     */
    class Transaction : public Serializable {
    public:

//        std::any acceptSerializator() override;
//
//        const transaction::Input& getInput(size_t index) const;
//        const transaction::Input& getInput(common::types::hash_t index) const;
//
//        const transaction::Input& getOutput(size_t index) const;
//        const transaction::Input& getOutput(common::types::hash_t index) const;


        ~Transaction() override = default;

        bool operator==(const Transaction &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Transaction &tx,
                                                    unsigned int version);

        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::list<uptr_t<input_t>> inputs_; //!< Ordered list of inputs. The order determines the order of signatures

        std::list<uptr_t<output_t>> outputs_; //!< Ordered list of outputs. The order determines future usages as inputs.
    };
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::Transaction &tx,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(tx);
        ar & tx.inputs_;
        ar & tx.outputs_;
    }
}

#endif //CHASM_TRANSACTION_H
