//
// Created by Daniel Bigos on 12.11.18.
//

//#include <chasm/primitives/Block.hpp>

struct A;
struct B;

namespace chasm::serialization {
//    using namespace chasm::primitives;

    template<>
    void Serializer::serialize_fields(Serializer::buffer_t &buffer, A const &obj) {
        std::cout << "hello\n";
    }

    template<>
    void Serializer::serialize_fields(Serializer::buffer_t &buffer, B const &obj) {
        std::cout << "hello 2\n";
    }

}

