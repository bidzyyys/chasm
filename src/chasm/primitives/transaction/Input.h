//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_INPUT_H
#define CHASM_INPUT_H

#include <cstdint>
#include <boost/optional.hpp>
#include <chasm/common/types.h>
#include "TXO.h"


namespace chasm::primitives::transaction {

    /*!
     * \brief Input of a transaction
     *
     * In a valid transaction this represents an UTXO to be used in the transaction.
     * The signature must sign the whole transaction (serialized), besides the signature itself.
     */
    struct Input : public DTO {

        std::any acceptSerializator() override;

        ~Input() override = default;

        TXO utxo; //!< A transaction output. The transaction is invalid unless this field is an UTXO.
        chasm::common::types::signature_t signature;
    };

}


#endif //CHASM_INPUT_H
