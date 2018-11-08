//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_TRANSACTION_H
#define CHASM_TRANSACTION_H

#include <list>
#include <chasm/primitives/transaction/Output.h>
#include "transaction/Input.h"
#include "Serializable.h"

namespace chasm::primitives {

    /*!
     * \brief Basic transaction
     */
    class Transaction : public Serializable {
    public:

        std::any acceptSerializator() override;

        const transaction::Input& getInput(size_t index) const;
        const transaction::Input& getInput(common::types::hash_t index) const;

        const transaction::Input& getOutput(size_t index) const;
        const transaction::Input& getOutput(common::types::hash_t index) const;


        ~Transaction() override = default;

    private:
        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::list<std::unique_ptr<input_t>> inputs_;
        std::list<std::unique_ptr<output_t>> outputs_;
    };
}


#endif //CHASM_TRANSACTION_H
