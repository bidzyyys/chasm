//
// Created by Daniel Bigos on 24.11.18.
//

#include <boost/test/unit_test_suite.hpp>
#include <boost/test/test_tools.hpp>
#include "chasm/ui/UI.h"

using namespace chasm::ui;

struct BytesAndHex {

    std::array<std::byte, 3> arr_bytes{(std::byte)'a', (std::byte)'b', (std::byte)'c'};

    const std::string hex{"616263"};
};

BOOST_AUTO_TEST_SUITE(ui_tests)

    BOOST_FIXTURE_TEST_CASE(bytesToHexStringTest, BytesAndHex) {

        BOOST_REQUIRE_EQUAL(bytesToHexString(arr_bytes), hex);
    }

BOOST_AUTO_TEST_SUITE_END()