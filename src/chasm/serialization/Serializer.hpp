//
// Created by Daniel Bigos on 12.11.18.
//

#ifndef CHASM_SERIALIZER_H
#define CHASM_SERIALIZER_H

#include <cstdint>
#include <type_traits>
#include <vector>
#include <iostream>
#include "traits.hpp"
#include "Archive.hpp"


namespace chasm::serialization {

    using namespace chasm;
    using namespace traits::classes;
    using namespace traits::inheritance;

    class Serializer {
    public:
        template<typename T>
        std::vector<std::byte> serialize(T const &obj) {
            OArchive a(*this);
            serialize(a, obj, inheritance_trait_t<T>());
            return a.getBuffer();
        }

    private:
        friend class Archive;

        template<typename T>
        void acceptReturn(Archive &archive, T const &obj) {
            serialize(archive, obj, inheritance_trait_t<T>());
        }

        template<typename Archive, typename T>
        void serialize(Archive &a, T const &obj, is_root_t) {
            a & static_cast<std::byte>(class_id_trait<T>::value);
            serialize_fields(a, obj);
        }

//        template<
//                typename Archive,
//                typename T,
//                typename B,
//                typename = typename std::enable_if_t<
//                        std::is_base_of_v<B, T> && !std::is_same_v<B, T>
//                >
//        >
//        void serialize(Archive &archive, T const &obj, buffer_t &buffer, is_derived_t<B>) {
//
//            archive & static_cast<std::byte>(classes::class_id_trait<T>::value)
//            & static_cast<B const &>(obj), buffer, inheritance::inheritance_trait_t<B>();
//
//            serialize_fields(archive, obj);
//
//        }
//
        template<typename Archive, typename T>
        void serialize_fields(Archive &archive, T const &obj);

//
    };

}

#include "Serializer.tpp"

#endif //CHASM_SERIALIZER_H
