//
// Created by Piotr Żelazko on 18/11/2018.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>


#include <chasm/serialization/Serializer.hpp>

using namespace chasm::serialization;

struct SimpleSerializable {
    explicit SimpleSerializable(std::byte aByte) : aByte(aByte) {}

    std::byte aByte;

    using class_id_e = serialization::traits::classes::class_id;
    using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Transaction>;

    using inheritance_t = serialization::traits::inheritance::is_root_t;
};

struct CompoundSerializable {

    SimpleSerializable simple;
    std::vector<SimpleSerializable> vect;
    std::vector<std::unique_ptr<SimpleSerializable>> ptr_vect;

    using class_id_e = serialization::traits::classes::class_id;
    using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Input>;

    using inheritance_t = serialization::traits::inheritance::is_root_t;
};

struct DerivedSerializable : public SimpleSerializable {

    explicit DerivedSerializable(std::byte aByte) : SimpleSerializable(aByte) {}

    using class_id_e = serialization::traits::classes::class_id;
    using class_id_t = serialization::traits::classes::class_id_t<class_id_e::Output>;

    using inheritance_t = serialization::traits::inheritance::is_derived_t<SimpleSerializable>;
};

namespace chasm::serialization {

    template<typename Ar>
    struct Serializer::Worker<Ar, SimpleSerializable> {
        void serialize_fields(Ar &archive, SimpleSerializable const &obj) {
            archive & obj.aByte;
        }
    };

    template<typename Ar>
    struct Serializer::Worker<Ar, CompoundSerializable> {
        void serialize_fields(Ar &archive, CompoundSerializable const &obj) {
            archive & obj.simple & obj.vect & obj.ptr_vect;
        }
    };

    template<typename Ar>
    struct Serializer::Worker<Ar, DerivedSerializable> {
        void serialize_fields(Ar &archive, DerivedSerializable const &obj) {}
    };
}

BOOST_AUTO_TEST_SUITE(serialization_of_primitives_and_compounds)

    struct EnvFixture {
        EnvFixture() {}

        OArchive o;
    };

    template<typename T>
    void compare_vectors(std::vector<T> const &input, std::vector<std::byte> const &result,
                         std::function<std::byte(T const &)> converter = [](T const &obj) { return obj; }) {

        x_size_t serializedSize = 0;
        BOOST_REQUIRE_GE(result.size(), sizeof(x_size_t));

        auto resultIt = result.begin();
        for (auto i = 0; i < sizeof(x_size_t); ++i, ++resultIt)
            serializedSize |= (static_cast<x_size_t>(*resultIt) << 8 * i);

        BOOST_REQUIRE_EQUAL(serializedSize + sizeof(x_size_t), result.size());
        BOOST_REQUIRE_EQUAL(serializedSize, input.size());

        for (auto it = input.begin(); it != input.end(); ++resultIt, ++it)
            BOOST_CHECK(*resultIt == converter(*it));

    }

    BOOST_FIXTURE_TEST_CASE(serializes_a_byte, EnvFixture) {
        std::byte b{0x11};
        o &b;
        BOOST_CHECK(b == o.getBuffer().at(0));
    }


    BOOST_FIXTURE_TEST_CASE(serializes_integers, EnvFixture) {


        union {
            uint8_t bytes[15];
            struct {
                uint64_t int64;
                uint32_t int32;
                uint16_t int16;
                uint8_t int8;
            } aStruct;
        } anUnion;

        anUnion.aStruct.int8 = 0x01;
        anUnion.aStruct.int16 = 0x0201;
        anUnion.aStruct.int32 = 0x04030201;
        anUnion.aStruct.int64 = 0x0807060504030201;

        [[maybe_unused]] auto &_r =
                o & anUnion.aStruct.int64 & anUnion.aStruct.int32 & anUnion.aStruct.int16 & anUnion.aStruct.int8;

        auto result = o.getBuffer();

        BOOST_CHECK_EQUAL(sizeof(anUnion.bytes), result.size());
        for (auto i = 0; i < sizeof(anUnion.bytes); ++i)
            BOOST_CHECK(anUnion.bytes[i] == static_cast<uint8_t>(result.at(i)));

    }

    BOOST_FIXTURE_TEST_CASE(serializes_an_array_of_bytes, EnvFixture) {

        std::array<std::byte, 32> array{};
        for (auto i = 0; i < array.size(); ++i) array.at(i) = std::byte(i);

        [[maybe_unused]] auto &_r = o & array;

        auto result = o.getBuffer();

        BOOST_CHECK_EQUAL(result.size(), array.size());
        for (auto i = 0; i < array.size(); ++i) BOOST_CHECK(result.at(i) == array.at(i));
    }


    BOOST_FIXTURE_TEST_CASE(serializes_a_vector_of_bytes, EnvFixture) {
        std::vector<std::byte> vec;

        for (auto i = 0; i < 32; ++i) vec.push_back(std::byte(i));

        [[maybe_unused]] auto &_r = o & vec;

        compare_vectors(vec, o.getBuffer());

    }

    BOOST_FIXTURE_TEST_CASE(serializes_a_vector_of_unique_ptrs_of_bytes, EnvFixture) {
        std::vector<std::unique_ptr<std::byte>> vec;

        for (auto i = 0; i < 32; ++i) vec.push_back(std::make_unique<std::byte>(std::byte(i)));

        [[maybe_unused]] auto &_r = o & vec;
        auto result = o.getBuffer();

        std::function<std::byte(std::unique_ptr<std::byte> const &)> converter = [](
                std::unique_ptr<std::byte> const &obj) -> std::byte { return *obj; };

        compare_vectors(vec, result, converter);

    }

    BOOST_FIXTURE_TEST_CASE(serializes_a_simple_class, EnvFixture) {
        SimpleSerializable obj{std::byte(0xfa)};
        std::vector<std::byte> expected{std::byte(0x01), std::byte(0xfa)};

        [[maybe_unused]] auto &_r = o & obj;

        auto result = o.getBuffer();
        BOOST_CHECK(expected == result);

    }

    BOOST_FIXTURE_TEST_CASE(serializes_a_compund_serializable, EnvFixture) {

        std::vector<std::unique_ptr<SimpleSerializable>> ptr_vec;
        ptr_vec.emplace_back(std::make_unique<SimpleSerializable>(std::byte(0xfc)));

        CompoundSerializable obj{SimpleSerializable(std::byte(0xfa)), {SimpleSerializable{std::byte(0xfb)}},
                                 std::move(ptr_vec)};
        std::vector<std::byte> expected{std::byte(0x02), std::byte(0x01), std::byte(0xfa),
                                        std::byte(0x01), std::byte(0x00), std::byte(0x01), std::byte(0xfb),
                                        std::byte(0x01), std::byte(0x00), std::byte(0x01), std::byte(0xfc)
        };

        [[maybe_unused]] auto &_r = o & obj;

        auto result = o.getBuffer();
        BOOST_CHECK(expected == result);

    }

    BOOST_FIXTURE_TEST_CASE(serializes_a_derived_class, EnvFixture) {
        DerivedSerializable d(std::byte(0x0f));

        std::vector<std::byte> expected{std::byte(0x03), std::byte(0x01), std::byte(0x0f)};

        [[maybe_unused]] auto &_r = o & d;

        auto result = o.getBuffer();

        BOOST_CHECK(expected == result);

    }


BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK
