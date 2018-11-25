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
        TXO(hash_t const& txHash, out_idx_t index);
        TXO(hash_t&& txHash, out_idx_t index);

        const hash_t &getTxHash() const;

        out_idx_t getIndex() const;

        bool operator==(const TXO &rh) const;

        virtual ~TXO() = default;

    private:
        hash_t txHash_; //!< Pointer to an existing transaction

        out_idx_t index_; //!< Index of the output

    };
}

#endif //CHASM_UTXO_H
