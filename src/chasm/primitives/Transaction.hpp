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
        using class_id_e = serialization::traits::classes::class_id;
        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Transaction>;

        using inheritance_t = serialization::traits::inheritance::is_root_t;



        void addInput(hash_t const &txHash, in_idx_t input);

        void addInput(hash_t &&txHash, in_idx_t input);

        void addOutput(value_t value, address_t const &receiver);

//        void addOutput(value_t value, address_t &&receiver);
//
//        void addOutput(value_t value, hash_t const &offerHash);
//
//        void addOutput(value_t value, hash_t &&offerHash);

        const transaction::Input &getInput(x_size_t index) const;

        const transaction::Output &getOutput(x_size_t index) const;

        virtual ~Transaction() = default;

    private:
        friend class chasm::serialization::Serializer;

        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::vector<uptr_t<input_t>> inputs_; //!< Ordered list of inputs. The order determines the order of signatures

        std::vector<uptr_t<output_t>> outputs_; //!< Ordered list of outputs. The order determines future usages as inputs.
    };
}

#endif //CHASM_TRANSACTION_H
