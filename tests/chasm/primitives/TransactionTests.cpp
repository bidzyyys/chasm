//
// Created by Daniel Bigos on 12.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/primitives/Transaction.hpp"

using namespace chasm::primitives;
using namespace chasm::types;

BOOST_AUTO_TEST_SUITE(primitives_transaction)


    BOOST_AUTO_TEST_CASE(sample_test){
        BOOST_REQUIRE_EQUAL(1,1);
    }


BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK