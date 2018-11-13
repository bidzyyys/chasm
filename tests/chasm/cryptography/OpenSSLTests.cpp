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
        auto hash_array = openSSL->generateSHA256(std::array<std::byte, 10>());
        auto hash_vector = openSSL->generateSHA256(std::vector<std::byte>(10));
        auto hash_list = openSSL->generateSHA256(std::list<std::byte>(10));
        BOOST_REQUIRE_EQUAL(hash_array.size(),SHA256_DIGEST_LENGTH);
        BOOST_REQUIRE_EQUAL(hash_vector.size(),SHA256_DIGEST_LENGTH);
        BOOST_REQUIRE_EQUAL(hash_list.size(),SHA256_DIGEST_LENGTH);
    }


BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK