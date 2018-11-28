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

        db.open(db_name);
    }

    const std::string db_name = "testdb";
    const bytes_t data{(std::byte)'1',(std::byte)'2',(std::byte)'3'};
    hash_t hash{};
    Database db;
};

struct UpdateData : public TestsData {

    UpdateData() = default;

    const bytes_t update_data{(std::byte)'a'};
};

BOOST_AUTO_TEST_SUITE(database)

    BOOST_FIXTURE_TEST_CASE(HandleConnectionsNoThrowTest, TestsData) {

        BOOST_CHECK_NO_THROW(db.close());
        BOOST_CHECK_NO_THROW(db.open(db_name));
        BOOST_CHECK_NO_THROW(db.close());
    }

    BOOST_FIXTURE_TEST_CASE(ReplaceConnectionNoThrowTest, TestsData) {

        BOOST_CHECK_NO_THROW(db.open(db_name));
        BOOST_CHECK_NO_THROW(db.open(db_name));
    }

    BOOST_FIXTURE_TEST_CASE(DataOperationWhileDisconnectedThrowTest, TestsData) {

        db.close();
        BOOST_CHECK_THROW(db.insertRecord(hash, data), DatabaseError);
        BOOST_CHECK_THROW(db.selectRecord(hash), DatabaseError);
        BOOST_CHECK_THROW(db.deleteRecord(hash), DatabaseError);
    }

    BOOST_FIXTURE_TEST_CASE(DeleteNonexistentRecordNoThrowTest, TestsData) {

        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
    }

    BOOST_FIXTURE_TEST_CASE(SelectNonexistentRecordTest, TestsData) {

        BOOST_REQUIRE(db.selectRecord(hash) == std::nullopt);
    }

    BOOST_FIXTURE_TEST_CASE(DataStorageTest, TestsData) {

        BOOST_CHECK_NO_THROW(db.insertRecord(hash, data));
        BOOST_REQUIRE(db.selectRecord(hash).value() == data);
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
        BOOST_REQUIRE(db.selectRecord(hash) == std::nullopt);
    }

    BOOST_FIXTURE_TEST_CASE(UpdateTest, UpdateData) {

        db.insertRecord(hash, data);
        BOOST_CHECK_NO_THROW(db.insertRecord(hash, update_data));
        BOOST_REQUIRE(db.selectRecord(hash).value() == update_data);
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
    }

    BOOST_FIXTURE_TEST_CASE(DataPersistenceTest, TestsData) {

        db.insertRecord(hash, data);
        db.close();
        db.open(db_name);
        BOOST_REQUIRE(db.selectRecord(hash).value() == data);
        BOOST_CHECK_NO_THROW(db.deleteRecord(hash));
    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK