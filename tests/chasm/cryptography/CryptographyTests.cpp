//
// Created by Daniel Bigos on 13.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/cryptography/Cryptography.hpp"
#include "chasm/ui/UI.h"

using namespace chasm::cryptography;
using namespace chasm::types;
using namespace chasm::ui;

struct Crypto {

    Crypto() {
        crypto = std::make_unique<Cryptography>();
    }

    std::unique_ptr<Cryptography> crypto;
};

struct TestData : public Crypto {

    std::vector<std::byte> bytes = {(std::byte)'a', (std::byte)'b', (std::byte)'c'};

    std::string str = "abc";

    std::array<char, 3> arr_char{'a', 'b', 'c'};

    std::vector<char> vec_char{'a', 'b', 'c'};
};

struct Hash : public Crypto {

    const std::unordered_map<std::string, std::string> test_hashes {
            { "abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" },
            { "aaa", "9834876dcfb05cb167a5c24953eba58c4ac89b1adf57f28f2f9d09af107ee8f0" },
            { "696969test696969", "f0bf342861f69c6c48d5875fd29da7dac03cad5ed10366da8c57a9035dc22c27" },
            { "123456789", "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225" }
    };
};

BOOST_FIXTURE_TEST_SUITE(cryptography, TestData)

    BOOST_AUTO_TEST_CASE(toBytesTest) {

        BOOST_REQUIRE(bytes == crypto->toBytes(str));
        BOOST_REQUIRE(bytes == crypto->toBytes(arr_char));
        BOOST_REQUIRE(bytes == crypto->toBytes(vec_char));
    }

    BOOST_FIXTURE_TEST_CASE(sha256Test, Hash) {

        for (const auto &ref_hash : test_hashes) {
            auto data = crypto->toBytes(ref_hash.first);
            hash_t hash_bytes;
            BOOST_CHECK_NO_THROW(hash_bytes = crypto->sha256(data));
            auto hash_hex = bytesToHexString(hash_bytes);
            BOOST_REQUIRE_EQUAL(hash_hex, ref_hash.second);
        }
    }

    BOOST_AUTO_TEST_CASE(SignatureTests) {

        key_pair_t key_pair;
        BOOST_CHECK_NO_THROW(key_pair = crypto->generateECDHKeyPair());
        auto signature = crypto->sign(key_pair.first, bytes);
        BOOST_REQUIRE(crypto->isValidSignature(key_pair.second, signature, bytes));
    }


BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK