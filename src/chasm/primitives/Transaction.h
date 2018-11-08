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

    /*! \brief Basic transaction
     *
     *  This is a DTO type.
     */
    struct Transaction : public DTO {
        using input_t = transaction::Input;
        using output_t = transaction::Output;

        std::any acceptSerializator() override;

        ~Transaction() override = default;

        std::list<input_t> inputs;
        std::list<output_t> outputs;
    };
}


#endif //CHASM_TRANSACTION_H
