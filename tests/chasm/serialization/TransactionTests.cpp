//
// Created by Piotr Żelazko on 18/11/2018.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include <chasm/primitives/Transaction.hpp>
#include <chasm/serialization/Serializer.hpp>

using namespace chasm::primitives;
using namespace chasm::types;
using namespace chasm::serialization;

//TODO: deserialization

BOOST_AUTO_TEST_SUITE(transaction_serialization)

    hash_t getSomeHash(){
        hash_t hash;

        for (size_t i = 0; i < hash.size(); ++i) hash.at(i) = std::byte(i);

        return hash;
    }

    address_t getSomeAddress(){
        address_t address;

        for (size_t i = 0; i < address.size(); ++i) address.at(i) = std::byte(i);

        return address;
    }

    struct EmptyTransactionFixture {

        Transaction transaction;
        bytes_t serialized{std::byte(static_cast<uint8_t>(class_id::Transaction)),
                           std::byte(0x00), std::byte(0x00),
                           std::byte(0x00), std::byte(0x00)};

    };

    struct TransactionWithSingleInputAndOutput{

        TransactionWithSingleInputAndOutput() {

            auto hash = getSomeHash();
            auto address = getSomeAddress();

            transaction.addInput(getSomeHash(), 1);
            transaction.addOutput(54321, getSomeAddress());

            serialized.insert(serialized.begin() + 4, hash.begin(), hash.end());
            serialized.insert(serialized.end(), address.begin(), address.end());
        }

        Transaction transaction;

        bytes_t serialized {std::byte(static_cast<uint8_t>(class_id::Transaction)),
                           std::byte(0x01), std::byte(0x00), std::byte(static_cast<uint8_t>(class_id::Input)),
                           std::byte(0x01), std::byte(0x00), std::byte(static_cast<uint8_t>(class_id::SimpleOutput)),
                           std::byte(static_cast<uint8_t>(class_id::Output)), std::byte(0x31), std::byte(0xd4)
        };

    };


//    BOOST_FIXTURE_TEST_CASE(empty_transaction, EmptyTransactionFixture){
//        BOOST_CHECK(serialized == Serializer().serialize(transaction));
//    }

//    BOOST_FIXTURE_TEST_CASE(simple_transfer_transaction, TransactionWithSingleInputAndOutput, *boost::unit_test::disabled()){
//
//        std::vector<std::byte> result = Serializer().serialize(transaction);
//
//        BOOST_CHECK(serialized == result);
//    }



BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LINK
