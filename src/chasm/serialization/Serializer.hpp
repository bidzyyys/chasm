//
// Created by Daniel Bigos on 12.11.18.
//

#ifndef CHASM_SERIALIZER_H
#define CHASM_SERIALIZER_H

#include <cstdint>
#include <type_traits>
#include <vector>
#include <iostream>


namespace chasm::serialization {

    namespace classes {
        enum class class_id : uint8_t {
            Block,
        };

        template<class_id id>
        struct class_id_t {
            static const class_id value = id;
        };

        template <typename T>
        struct class_id_trait{
            using type = typename T::class_id_t;
            static const class_id value = type::value;
        };
    }
    namespace inheritance {
        struct is_root_t {};

        template<typename Base>
        struct is_derived_t {};

        template <typename T>
        struct inheritance_trait{
            using type = typename T::inheritance_t;
        };

        template <typename T>
        using  inheritance_trait_t = typename inheritance_trait<T>::type;
    }

    class Serializer {
    public:
        template <typename T>
        std::vector<std::byte> serialize(T const& obj){
            buffer_t buffer;
            serialize(obj, buffer, inheritance::inheritance_trait_t<T>());
            return buffer;
        }

    private:
        using buffer_t = std::vector<std::byte>;

        template <typename T>
        void serialize(T const& obj, buffer_t& buffer, inheritance::is_root_t){
            buffer.push_back(static_cast<std::byte>(classes::class_id_trait<T>::value));
            serialize_fields(buffer, obj);
        }

        template <typename T,
                  typename B,
                  typename = typename std::enable_if_t<
                          std::is_base_of_v<B, T> && !std::is_same_v<B,T>
                          >
                  >
        void serialize(T const& obj, buffer_t& buffer, inheritance::is_derived_t<B>){

            buffer.push_back(static_cast<std::byte>(classes::class_id_trait<T>::value));
            serialize(static_cast<B const&>(obj), buffer, inheritance::inheritance_trait_t<B>());
            serialize_fields(buffer, obj);

        }

#pragma clang diagnostic push
#pragma ide diagnostic ignored "NotImplementedFunctions"
        template <typename T>
        void serialize_fields(Serializer::buffer_t& buffer, T const& obj);
#pragma clang diagnostic pop

    };

}

#include "Serializer.tpp"
#endif //CHASM_SERIALIZER_H
