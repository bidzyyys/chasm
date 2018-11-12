//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_MINING_TRANSACTION_H
#define CHASM_MINING_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>

namespace chasm::primitives::transaction {
    class MiningTransaction;
}

namespace boost::serialization {
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::MiningTransaction &tx,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction of type mining.
     *
     * This transaction has no inputs and should produce \i XPC tokens.
     * Starting from 50.0 per block and halving each 10^6 blocks.
     * This is also the place, where fees from other transactions can be collected.
     * In each block can exist only one transaction of this type and must be placed as the first one.
     */
    class MiningTransaction : public Transaction {
    public:

        ~MiningTransaction() override = default;

        bool operator==(const MiningTransaction &rh) const;

    private:
        friend class boost::serialization::access;

        template <typename Archive>
        friend void boost::serialization::serialize(Archive &ar, MiningTransaction &tx,
                       unsigned int version);

    };
}

namespace boost::serialization{
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::MiningTransaction &tx,
                   unsigned int version){
        ar & boost::serialization::base_object<chasm::primitives::Transaction>(tx);
    }
}

#endif //CHASM_MINING_TRANSACTION_H
