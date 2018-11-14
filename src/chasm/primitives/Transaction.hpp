//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TRANSACTION_H
#define CHASM_TRANSACTION_H

#include <list>
#include <chasm/primitives/transaction/Output.hpp>
#include "chasm/primitives/transaction/Input.hpp"


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

    private:

        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::list<uptr_t<input_t>> inputs_; //!< Ordered list of inputs. The order determines the order of signatures

        std::list<uptr_t<output_t>> outputs_; //!< Ordered list of outputs. The order determines future usages as inputs.
    };
}

#endif //CHASM_TRANSACTION_H
