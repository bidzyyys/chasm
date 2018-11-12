//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_INPUT_H
#define CHASM_INPUT_H

#include <cstdint>
#include <boost/optional.hpp>
#include <chasm/types.hpp>
#include "TXO.hpp"

namespace chasm::primitives::transaction {
    class Input;
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::Input &input,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Input of a transaction
     *
     * In a valid transaction this represents an UTXO to be used in the transaction.
     */
    class Input : public Serializable {
    public:

//        std::any acceptSerializator() override;

        ~Input() override = default;

        bool operator==(const Input &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Input &input,
                                                    unsigned int version);

        TXO utxo_; //!< A transaction output. The transaction is invalid unless this field is an UTXO.
    };

}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::Input &input,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(input);
        ar & input.utxo_;
    }
}

#endif //CHASM_INPUT_H
