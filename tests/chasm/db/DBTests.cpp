//
// Created by Daniel Bigos on 24.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/db/Database.h"

using namespace chasm::db;

struct TestsData {

    const std::string db_name = "testdb";
    Database db;
};

BOOST_FIXTURE_TEST_SUITE(DatabaseTests, TestsData)

    BOOST_AUTO_TEST_CASE(OpenConnectionNoThrowTest) {

        BOOST_CHECK_NO_THROW(db.open(db_name));
        //check whether connection is properly replaced
        BOOST_CHECK_NO_THROW(db.open(db_name));
        BOOST_CHECK_NO_THROW(db.close());
    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK