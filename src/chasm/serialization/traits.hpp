//
// Created by Piotr Żelazko on 15/11/2018.
//

#ifndef CHASM_TRAITS_HPP
#define CHASM_TRAITS_HPP

#include <cstdint>

namespace chasm::serialization::traits {
    namespace classes {
        enum class class_id : uint8_t {
            Block,
            Transaction,
            Input, Output,

        };

        template<class_id id>
        struct class_id_t {
            static const class_id value = id;
        };

        template<typename T>
        struct class_id_trait {
            using type = typename T::class_id_t;
            static const class_id value = type::value;
        };

        template <typename T>
        using class_id_trait_t = typename class_id_trait<T>::type;
    }
    namespace inheritance {
        struct is_root_t {
        };

        template<typename Base>
        struct is_derived_t {
        };

        template<typename T>
        struct inheritance_trait {
            using type = typename T::inheritance_t;
        };

        template<typename T>
        using inheritance_trait_t = typename inheritance_trait<T>::type;
    }

}

namespace chasm::serialization{
    class Serializer;
}


#endif //CHASM_TRAITS_HPP
