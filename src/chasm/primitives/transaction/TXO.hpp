//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_UTXO_H
#define CHASM_UTXO_H

#include <chasm/types.hpp>


namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction output
     */
    class TXO {
    public:

//        ~TXO() override = default;

        bool operator==(const TXO &rh) const;

    private:
        hash_t txHash_; //!< Pointer to an existing transaction

        out_idx_t index_; //!< Index of the output

    };
}

#endif //CHASM_UTXO_H
