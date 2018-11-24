//
// Created by Daniel Bigos on 24.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/db/Database.h"

using namespace chasm::db;

struct TestsData {

};

BOOST_FIXTURE_TEST_SUITE(DatabaseTests, TestsData)

    BOOST_AUTO_TEST_CASE(SampleTest) {

        Database database;
        BOOST_REQUIRE_EQUAL(1, 1);
    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK