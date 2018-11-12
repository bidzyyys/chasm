//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_UTXO_H
#define CHASM_UTXO_H

#include <chasm/common/types.hpp>
#include <chasm/primitives/Serializable.hpp>

namespace chasm::primitives::transaction{
    class TXO;
}

namespace boost::serialization{
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::TXO &txo,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction output
     */
    class TXO : public Serializable {
    public:

        ~TXO() override = default;

        bool operator==(const TXO &rh) const;

    private:
        friend class boost::serialization::access;

        template <typename Archive>
        friend void boost::serialization::serialize(Archive &ar, TXO &txo,
                                                    unsigned int version);

        chasm::common::types::hash_t txHash_; //!< Pointer to an existing transaction

        chasm::common::types::out_idx_t index_; //!< Index of the output

    };
}

namespace boost::serialization{
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::TXO &txo,
                    unsigned int version){
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(txo);
        ar & txo.txHash_;
        ar & txo.index_;
    }
}

BOOST_CLASS_EXPORT(chasm::primitives::transaction::TXO)

#endif //CHASM_UTXO_H
