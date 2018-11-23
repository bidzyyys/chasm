//
// Created by Daniel Bigos on 12.11.18.
//

#include <type_traits>
#include <chasm/primitives/Block.hpp>
#include <chasm/primitives/Transaction.hpp>

namespace chasm::serialization {

    template<typename T>
    std::vector<std::byte> Serializer::serialize(T const &obj) {
        OArchive a;
        serialize(a, obj, inheritance_trait_t<T>());
        return a.getBuffer();
    }

    template<typename Ar, typename T>
    void Serializer::serialize(Ar &a, T const &obj, is_root_t) {
        a & static_cast<std::byte>(class_id_trait<T>::value);
        Worker<Ar, T>().serialize_fields(a, obj);
    }

    template <typename Ar, typename T, typename B>
    void Serializer::serialize(Ar& a, T const& obj, is_derived_t<B>){
        a & static_cast<std::byte>(class_id_trait<T>::value) & static_cast<B const&>(obj);
        Worker<Ar, T>().serialize_fields(a, obj);
    }

    template<typename T>
    void Serializer::acceptReturn(OArchive &archive, T const &obj) {
        serialize(archive, obj, inheritance_trait_t<T>());
    }

/// WORKERS
    template<typename Ar>
    struct Serializer::Worker<Ar, primitives::Block> {
        void serialize_fields(Ar &archive, primitives::Block const &obj) {

            archive & obj.getPrevTxHash()
            & obj.getMerkleTreeRoot()
            & obj.getTimestamp()
            & obj.getNonce()
            & obj.getDifficulty();
        }
    };

    template<typename Ar>
    struct Serializer::Worker<Ar, primitives::Transaction> {
        void serialize_fields(Ar &archive, primitives::Transaction const &obj) {
            archive & obj.inputs_ & obj.outputs_;
        }
    };


}

