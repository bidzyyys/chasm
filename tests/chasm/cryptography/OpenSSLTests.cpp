//
// Created by Daniel Bigos on 13.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/cryptography/OpenSSL.hpp"

using namespace chasm::cryptography;

BOOST_AUTO_TEST_SUITE(cryptography)

    auto openSSL = std::make_unique<OpenSSL>();

    BOOST_AUTO_TEST_CASE(simple_test){
        auto hash_array = openSSL->sha256(std::array<std::byte, 10>());
        auto hash_vector = openSSL->sha256(std::vector<std::byte>(10));
        auto hash_list = openSSL->sha256(std::list<std::byte>(10));
        BOOST_REQUIRE_EQUAL(hash_array.size(), HASH256);
        BOOST_REQUIRE_EQUAL(hash_vector.size(), HASH256);
        BOOST_REQUIRE_EQUAL(hash_list.size(), HASH256);
    }

    BOOST_AUTO_TEST_CASE(test) {
        auto test = openSSL->test();
        BOOST_REQUIRE_EQUAL(test.size(),HASH256);
    }
BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK