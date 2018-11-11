//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_UTXO_H
#define CHASM_UTXO_H

#include <chasm/common/types.h>
#include <chasm/primitives/Serializable.h>

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction output
     */
    class TXO : public Serializable {
    public:

        ~TXO() override = default;

    private:

        chasm::common::types::hash_t txHash_; //!< Pointer to an existing transaction
        chasm::common::types::out_idx_t index_; //!< Index of the output

    };
}

#endif //CHASM_UTXO_H
