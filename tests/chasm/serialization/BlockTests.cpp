//
// Created by Daniel Bigos on 12.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include <chasm/primitives/Block.hpp>
#include <chasm/serialization/Serializer.hpp>

using namespace chasm::primitives;
using namespace chasm::types;
using namespace chasm::serialization;

BOOST_AUTO_TEST_SUITE(block_serialization)


    hash_t getSomeHash() {
        hash_t someHash;
        uint8_t i = 0x00;
        for (auto &byte : someHash) byte = std::byte(++i);
        return someHash;
    }

    struct ZeroedBlockFixture {
        const Block block = {hash_t{}, hash_t{}, 0, 0, 0};
        const bytes_t serialized = std::vector<std::byte>(84, std::byte(0x00));
    };


    struct EmptyBlockFixture {
        EmptyBlockFixture() : block(getSomeHash(), getSomeHash(), timestamp, nonce, difficulty) {

            serialized.push_back(std::byte(class_id::Block));

            auto hash = getSomeHash();
            serialized.insert(serialized.end(), hash.begin(), hash.end());
            serialized.insert(serialized.end(), hash.begin(), hash.end());

            serialized.push_back(std::byte(timestamp));
            for (auto i = 1; i < sizeof(timestamp_t); ++i) serialized.push_back(std::byte(0x00));

            serialized.push_back(std::byte(nonce));
            for (auto i = 1; i < sizeof(nonce_t); ++i) serialized.push_back(std::byte(0x00));

            serialized.push_back(std::byte(difficulty));
            for (auto i = 1; i < sizeof(difficulty_t); ++i) serialized.push_back(std::byte(0x00));

            serialized.push_back(std::byte(0x00));
            serialized.push_back(std::byte(0x00));
        }

        static const uint8_t timestamp = 1;
        static const uint8_t nonce = 2;
        static const uint8_t difficulty = 3;

        Block block;
        bytes_t serialized;
    };

    BOOST_FIXTURE_TEST_CASE(zeroed_block_serialization, ZeroedBlockFixture, *boost::unit_test::disabled()) {

        auto result = Serializer::serialize(block);
        BOOST_CHECK(serialized == result);
    }

    BOOST_FIXTURE_TEST_CASE(empty_block_serialization, EmptyBlockFixture, *boost::unit_test::disabled()) {
        auto result = Serializer::serialize(block);
        BOOST_CHECK(serialized == result);
    }


BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK