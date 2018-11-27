//
// Created by Daniel Bigos on 24.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include "chasm/db/Database.hpp"

using namespace chasm::db;
using namespace chasm::types;

struct TestsData {

    TestsData() {

        hash.at(0) = static_cast<std::byte>('a');
    }

    const std::string db_name = "testdb";
    const bytes_t data{(std::byte)'1',(std::byte)'2',(std::byte)'3'};
    hash_t hash{};
    Database db;
};

BOOST_FIXTURE_TEST_SUITE(database, TestsData)

    BOOST_AUTO_TEST_CASE(OpenConnectionNoThrowTest) {

        BOOST_CHECK_NO_THROW(db.open(db_name));
        //check whether connection is properly replaced
        BOOST_CHECK_NO_THROW(db.open(db_name));
        BOOST_CHECK_NO_THROW(db.close());
    }

    BOOST_AUTO_TEST_CASE(DataStoragePipelineTest) {

        //check if throw exception when connection is closed
        db.close();
        BOOST_CHECK_THROW(db.insertRecord(hash, data), DatabaseError);
        BOOST_CHECK_THROW(db.selectRecord(hash), DatabaseError);
        BOOST_CHECK_THROW(db.deleteRecord(hash), DatabaseError);
        db.open(db_name);

        // delete record if exists
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
        BOOST_REQUIRE(db.selectRecord(hash) == std::nullopt);

        // insert record and check if exists
        BOOST_CHECK_NO_THROW(db.insertRecord(hash, data));
        BOOST_REQUIRE(db.selectRecord(hash).value() == data);

        // replace inserted record and then check
        BOOST_CHECK_NO_THROW(db.insertRecord(hash, data));
        BOOST_REQUIRE(db.selectRecord(hash).value() == data);

        // reopen connection
        db.close();
        db.open(db_name);

        // check if record still exists
        BOOST_REQUIRE(db.selectRecord(hash).value() == data);

        //delete record
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
        BOOST_REQUIRE(db.selectRecord(hash) == std::nullopt);
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK