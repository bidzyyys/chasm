//
// Created by Daniel Bigos on 11.11.18.
//

#ifndef CHASM_HEADER_H
#define CHASM_HEADER_H

#include <chasm/common/types.hpp>
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
    class Header : public Serializable {
    public:
        ~Header() override = default;

        bool operator==(const Header &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Header &header,
                                                    unsigned int version);

        common::types::hash_t prev_tx_hash_;

        common::types::hash_t merkle_tree_root_;

        uint64_t timestamp_; // TODO: must be higher than the timestamp of the previous block

        common::types::nonce_t nonce_;

        common::types::difficulty_t difficulty_;
    };
}


namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::Header &header,
                   unsigned int version) {
        ar & boost::serialization::base_object<chasm::primitives::Serializable>(header);
        ar & header.prev_tx_hash_;
        ar & header.merkle_tree_root_;
        ar & header.timestamp_;
        ar & header.nonce_;
        ar & header.difficulty_;
    }
}


BOOST_CLASS_EXPORT(chasm::primitives::Header)

#endif //CHASM_HEADER_H
