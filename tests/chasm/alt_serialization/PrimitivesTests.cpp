//
// Created by Piotr Żelazko on 25/11/2018.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include <chasm/types.hpp>
#include <chasm/serialization/Serializer.hpp>

using namespace chasm;
using namespace serialization;

BOOST_AUTO_TEST_SUITE(alt_serialization_of_primitives)

    template <typename T>
    void check_serialization(T const& obj, bytes_t const& expected){
        const auto serialized = Serializer().serialize(obj);
        BOOST_CHECK(serialized == expected);

        auto deserialized = Serializer().deserialize<T>(expected);
        BOOST_CHECK(deserialized == obj);
    }


    BOOST_AUTO_TEST_CASE(a_byte){
        const std::byte byte {0xab};
        const bytes_t expected {byte};

        check_serialization(byte, expected);
    }

    BOOST_AUTO_TEST_CASE(serializes_an_int){
        uint64_t value = 0xa1b2c3d4e5f6a7b8;
        bytes_t expected {std::byte(0xb8), std::byte(0xa7), std::byte(0xf6), std::byte(0xe5),
                          std::byte(0xd4), std::byte(0xc3), std::byte(0xb2), std::byte(0xa1)};


        check_serialization(value, expected);

    }

    BOOST_AUTO_TEST_CASE(serializes_a_ptr){
        const auto byte = std::make_unique<std::byte>(std::byte(0xab));
        const bytes_t expected {*byte};

        auto serialized = Serializer().serialize(byte);
        BOOST_CHECK(serialized == expected);

        auto deserialized = Serializer().deserialize<std::unique_ptr<std::byte>>(expected);
        BOOST_CHECK(*deserialized == *byte);

    }

    BOOST_AUTO_TEST_CASE(serializes_a_vector){
        const std::vector<uint8_t> data {1,2,3,4,5,6,7,8};
        std::vector<std::byte> expected {std::byte(data.size()), std::byte(0x00)};
        std::transform(data.begin(), data.end(), std::back_inserter(expected), [](auto byte){return std::byte(byte);});

        const auto serialized = Serializer().serialize(data);
        BOOST_CHECK(expected == serialized);

        auto deserialized = Serializer().deserialize<std::vector<uint8_t>>(expected);
        BOOST_CHECK(data == deserialized);
    }

    BOOST_AUTO_TEST_CASE(serializes_an_array){
        hash_t hash;
        for (uint8_t i = 0; i < hash.size(); ++i) hash.at(i) = std::byte(i);

        std::vector<std::byte> expected;
        std::transform(hash.begin(), hash.end(), std::back_inserter(expected), [](auto byte){return std::byte(byte);});

        const auto serialized = Serializer().serialize(hash);
        BOOST_CHECK(expected == serialized);

        auto deserialized = Serializer().deserialize<hash_t>(expected);
        BOOST_CHECK(hash == deserialized);
    }

BOOST_AUTO_TEST_SUITE_END()



#endif // BOOST_TEST_DYN_LINK