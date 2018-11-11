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
     */
    class Input : public Serializable {
    public:

        std::any acceptSerializator() override;

        ~Input() override = default;

    private:
        TXO utxo_; //!< A transaction output. The transaction is invalid unless this field is an UTXO.
    };

}


#endif //CHASM_INPUT_H
