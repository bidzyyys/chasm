//
// Created by Piotr Żelazko on 18/11/2018.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include <chasm/primitives/Transaction.hpp>

using namespace chasm::primitives;
using namespace chasm::types;
using namespace chasm::serialization;

BOOST_AUTO_TEST_SUITE(transaction_serialization)

    struct EmptyTransactionFixture {

        Transaction transaction;
        bytes_t serialized{std::byte(0x00), std::byte(0x00)};
    };


//    BOOST_FIXTURE_TEST_CASE(empty_transaction, EmptyTransactionFixture){
//        Serializer s;
//        auto result = s.serialize(transaction);
//        BOOST_CHECK(serialized == result);
//    }

BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK
