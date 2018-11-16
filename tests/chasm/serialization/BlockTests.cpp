//
// Created by Daniel Bigos on 12.11.18.
//

#define BOOST_TEST_DYN_LINK
#ifdef BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>
#include <chasm/primitives/Block.hpp>
#include <chasm/serialization/Serializer.hpp>

using namespace chasm::primitives;
using namespace chasm::types;
using namespace chasm::serialization;

BOOST_AUTO_TEST_SUITE(block_serialization)

    struct BlockFixture {
        BlockFixture() : zeroedBlock() {

        }

        const Block zeroedBlock;
        const bytes_t serializedZeroedBlock = std::vector<std::byte>(82, std::byte(0x00));
    };


    BOOST_FIXTURE_TEST_CASE(empty_block_serialization, BlockFixture) {
        BOOST_CHECK(serializedZeroedBlock == Serializer().serialize(zeroedBlock));
    }



BOOST_AUTO_TEST_SUITE_END()

#endif //BOOST_TEST_DYN_LKINK