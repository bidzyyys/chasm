//
// Created by Daniel Bigos on 13.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/cryptography/Cryptography.hpp"

using namespace chasm::cryptography;
using namespace chasm::types;

BOOST_AUTO_TEST_SUITE(cryptography)

    auto crypto = std::make_unique<Cryptography>();

    BOOST_AUTO_TEST_CASE(toBytesTest){
        std::vector<std::byte> bytes = {(std::byte)'a', (std::byte)'b', (std::byte)'c'};
        std::string str = "abc";
        std::array<char, 3> array{'a', 'b', 'c'};
        std::vector<char> vector{'a', 'b', 'c'};

        BOOST_REQUIRE(bytes == crypto->toBytes(str));
        BOOST_REQUIRE(bytes == crypto->toBytes(array));
        BOOST_REQUIRE(bytes == crypto->toBytes(vector));
    }

    BOOST_AUTO_TEST_CASE(bytesToHexStringTest){
        const std::string hex{"616263"};
        std::vector<std::byte> vector{(std::byte)'a', (std::byte)'b', (std::byte)'c'};
        std::array<std::byte, 3> array{(std::byte)'a', (std::byte)'b', (std::byte)'c'};

        BOOST_REQUIRE_EQUAL(crypto->bytesToHexString(vector), hex);
        BOOST_REQUIRE_EQUAL(crypto->bytesToHexString(array), hex);
    }

    BOOST_AUTO_TEST_CASE(cryptoLibSHA256NoThrowTest){
        BOOST_CHECK_NO_THROW(crypto->sha256(std::vector<std::byte>(10)));
    }

    BOOST_AUTO_TEST_CASE(SHA256VerificationOutput) {

        const std::unordered_map<std::string, std::string> test_hashes {
                { "abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" },
                { "aaa", "9834876dcfb05cb167a5c24953eba58c4ac89b1adf57f28f2f9d09af107ee8f0" },
                { "696969test696969", "f0bf342861f69c6c48d5875fd29da7dac03cad5ed10366da8c57a9035dc22c27" },
                { "123456789", "15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225" }
        };

        auto hash = crypto->sha256({(std::byte)'a', (std::byte)'b', (std::byte)'c'});
        BOOST_REQUIRE_EQUAL(hash.size(), HASH256);
        for(auto it = test_hashes.begin(); it != test_hashes.end(); ++it) {
            auto bytes = crypto->toBytes(it->first);
            auto hash = crypto->sha256(bytes);
            auto hex = crypto->bytesToHexString(hash);
            BOOST_REQUIRE_EQUAL(hex, it->second);
        }

    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK