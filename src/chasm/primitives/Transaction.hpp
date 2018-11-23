//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TRANSACTION_H
#define CHASM_TRANSACTION_H

#include <vector>
#include <chasm/serialization/traits.hpp>
#include "transaction/Output.hpp"
#include "transaction/Input.hpp"

namespace chasm::serialization {
    class Serializer;
}

namespace chasm::primitives {

    /*!
     * \brief Basic transaction
     */
    class Transaction {
    public:


//
//        const transaction::Input& getInput(size_t index) const;
//        const transaction::Input& getInput(common::types::hash_t index) const;
//
//        const transaction::Input& getOutput(size_t index) const;
//        const transaction::Input& getOutput(common::types::hash_t index) const;



        virtual ~Transaction() = default;

        bool operator==(const Transaction &rh) const;

        using class_id_e = serialization::traits::classes::class_id;
        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Transaction>;

        using inheritance_t = serialization::traits::inheritance::is_root_t;

    private:
        friend class chasm::serialization::Serializer;

        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::vector<uptr_t<input_t>> inputs_; //!< Ordered list of inputs. The order determines the order of signatures

        std::vector<uptr_t<output_t>> outputs_; //!< Ordered list of outputs. The order determines future usages as inputs.
    };
}

#endif //CHASM_TRANSACTION_H
