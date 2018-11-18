//
// Created by Daniel Bigos on 12.11.18.
//

#include <chasm/primitives/Block.hpp>
#include <type_traits>

namespace chasm::serialization {


    template<typename Archive,
            typename T>
    void Serializer::serialize_fields(Archive &archive, T const &obj) {
        archive & obj.getPrevTxHash() & obj.getMerkleTreeRoot() & obj.getTimestamp()  & obj.getNonce() & obj.getDifficulty();
    }
}

