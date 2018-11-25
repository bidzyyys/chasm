//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_INPUT_H
#define CHASM_INPUT_H

#include <cstdint>
#include <chasm/types.hpp>
#include <chasm/serialization/traits.hpp>
#include "TXO.hpp"

namespace chasm::primitives::transaction {

    /*!
     * \brief Input of a transaction
     *
     * In a valid transaction this represents an UTXO to be used in the transaction.
     */
    class Input {
    public:
        using class_id_e = serialization::traits::classes::class_id;
        using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Input>;
        using inheritance_t = serialization::traits::inheritance::is_root_t;

        Input(hash_t const& hash, in_idx_t index);
        Input(hash_t&& hash, in_idx_t index);

        const TXO &getUTXO() const;

        bool operator==(const Input &rh) const;

        virtual ~Input() = default;

    private:
        TXO utxo_; //!< A transaction output. The transaction is invalid unless this field is an UTXO.
    };

}

#endif //CHASM_INPUT_H
