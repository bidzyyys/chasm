//
// Created by Daniel Bigos on 11.11.18.
//

#ifndef CHASM_HEADER_H
#define CHASM_HEADER_H

#include <chasm/types.hpp>
#include "Serializable.hpp"

namespace chasm::primitives {
    class Header;
}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::Header &header,
                   unsigned int version);
}

namespace chasm::primitives {

    /*!
     * \brief Represents Block's header
     *
     * \b Note: Hash of the block is a hash of the header.
     */
    class Header : public Serializable {
    public:
        ~Header() override = default;

        bool operator==(const Header &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Header &header,
                                                    unsigned int version);

        hash_t prevTxHash_; //!< Pointer to the previous block

        hash_t merkleTreeRoot_; //!< Merkle tree root of a tree made of included transactions

        // TODO: must be higher than the timestamp of the previous block
        timestamp_t timestamp_; //!< Timestamp of the current block

        nonce_t nonce_; //!< Adjustable value. Used when mining new blocks

        difficulty_t difficulty_; //!< Number of leading bits of hash that must be zeroed
    };
}


namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::Header &header,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(header);
        ar & header.prevTxHash_;
        ar & header.merkleTreeRoot_;
        ar & header.timestamp_;
        ar & header.nonce_;
        ar & header.difficulty_;
    }
}

#endif //CHASM_HEADER_H
