//
// Created by Daniel Bigos on 12.11.18.
//

#ifndef CHASM_SERIALIZER_H
#define CHASM_SERIALIZER_H

#include <cstdint>
#include <type_traits>
#include <vector>
#include <iostream>
#include <chasm/types.hpp>
#include "traits.hpp"


namespace chasm::serialization {

    class OArchive;

    using namespace chasm;
    using namespace traits::classes;
    using namespace traits::inheritance;

    class Serializer {
    public:

        template<typename T>
        static std::vector<std::byte> serialize(T const &obj);

    private:
        friend class OArchive;

        template<typename T>
        static void acceptReturn(OArchive &archive, T const &obj);

        template<typename Ar, typename T>
        static void serialize(Ar &a, T const &obj, is_root_t);

        template <typename Ar, typename T, typename B>
        static void serialize(Ar& a, T const& obj, is_derived_t<B>);

        template<
                typename Ar,
                typename T
        >
        struct Worker {
            void serialize_fields(Ar &, T const &obj) const;
        };

    };

}

#include "Archive.hpp"

#include "Serializer.tpp"

#endif //CHASM_SERIALIZER_H
