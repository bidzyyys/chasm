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
        std::any acceptSerializator() override;

        ~TXO() override = default;

    private:

        //! Pointer to an existing transaction
        chasm::common::types::hash_t tx_hash_;
        //! Index of the output
        uint8_t index_;

    };
}

#endif //CHASM_UTXO_H
