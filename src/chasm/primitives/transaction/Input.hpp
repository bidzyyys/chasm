//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_INPUT_H
#define CHASM_INPUT_H

#include <cstdint>
#include <chasm/types.hpp>
#include "TXO.hpp"

namespace chasm::primitives::transaction {

    /*!
     * \brief Input of a transaction
     *
     * In a valid transaction this represents an UTXO to be used in the transaction.
     */
    class Input {
    public:

        virtual ~Input() = default;

        bool operator==(const Input &rh) const;

    private:
        TXO utxo_; //!< A transaction output. The transaction is invalid unless this field is an UTXO.
    };

}

#endif //CHASM_INPUT_H
