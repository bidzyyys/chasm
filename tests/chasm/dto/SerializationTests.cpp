//
// Created by Daniel Bigos on 08.11.18.
//

#include <boost/serialization/export.hpp>
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/test/unit_test_suite.hpp>
#include <boost/test/test_tools.hpp>
#include <boost/serialization/vector.hpp>
#include <chasm/dto/MatchDTO.h>
#include "chasm/dto/OfferDTO.h"

using namespace chasm::dto;

BOOST_CLASS_EXPORT_GUID(chasm::dto::TransactionDTO, "TransactionDTO")
BOOST_CLASS_EXPORT_GUID(chasm::dto::OfferDTO, "OfferDTO")
BOOST_CLASS_EXPORT_GUID(chasm::dto::MatchDTO, "MatchDTO")

BOOST_AUTO_TEST_SUITE(DTOIntegrationTests)

    BOOST_AUTO_TEST_CASE(CheckSerializationTransactioDTO) {
        std::string str;
        std::unique_ptr<TransactionDTO> pSrc = std::make_unique<TransactionDTO>(10);
        std::unique_ptr<TransactionDTO> pDst;
        {
            std::ostringstream ofs;
            boost::archive::binary_oarchive oa(ofs);
            oa << pSrc;
            str = ofs.str();
        }
        {
            std::istringstream ifs(str);
            boost::archive::binary_iarchive ia(ifs);
            ia >> pDst;
        }
        BOOST_REQUIRE(pDst != nullptr);
        BOOST_REQUIRE(*pSrc == *pDst);
    }

    BOOST_AUTO_TEST_CASE(CheckSerializationOfferDTO){
        std::string str;
        std::unique_ptr<TransactionDTO> pSrc = std::make_unique<OfferDTO>(10, 1.1);
        std::unique_ptr<TransactionDTO> pDst;
        {
            std::ostringstream ofs;
            boost::archive::binary_oarchive oa(ofs);
            oa << pSrc;
            str = ofs.str();
        }
        {
            std::istringstream ifs(str);
            boost::archive::binary_iarchive ia(ifs);
            ia >> pDst;
        }
        BOOST_REQUIRE(pDst != nullptr);
        BOOST_REQUIRE(*pSrc == *pDst);
    }

    BOOST_AUTO_TEST_CASE(CheckSerializationMatchDTO){
        std::string str;
        std::unique_ptr<TransactionDTO> pSrc = std::make_unique<MatchDTO>(10, false);
        std::unique_ptr<TransactionDTO> pDst;
        {
            std::ostringstream ofs;
            boost::archive::binary_oarchive oa(ofs);
            oa << pSrc;
            str = ofs.str();
        }
        {
            std::istringstream ifs(str);
            boost::archive::binary_iarchive ia(ifs);
            ia >> pDst;
        }
        BOOST_REQUIRE(pDst != nullptr);
        BOOST_REQUIRE(*pSrc == *pDst);
    }

    BOOST_AUTO_TEST_CASE(CheckSerialization){
        std::string str;
        std::unique_ptr<TransactionDTO> pTxSrc = std::make_unique<TransactionDTO>(10);
        std::unique_ptr<TransactionDTO> pTxDst;
        std::unique_ptr<TransactionDTO> pOfferSrc = std::make_unique<OfferDTO>(10, 1.1);
        std::unique_ptr<TransactionDTO> pOfferDst;
        std::unique_ptr<TransactionDTO> pMatchSrc = std::make_unique<MatchDTO>(10, false);
        std::unique_ptr<TransactionDTO> pMatchDst;
        {
            std::ostringstream ofs;
            boost::archive::binary_oarchive oa(ofs);
            oa << pTxSrc;
            oa << pOfferSrc;
            oa << pMatchSrc;
            str = ofs.str();
        }
        {
            std::istringstream ifs(str);
            boost::archive::binary_iarchive ia(ifs);
            ia >> pTxDst;
            ia >> pOfferDst;
            ia >> pMatchDst;
        }
        BOOST_REQUIRE(pTxDst != nullptr);
        BOOST_REQUIRE(*pTxSrc == *pTxDst);
        BOOST_REQUIRE(pOfferDst != nullptr);
        BOOST_REQUIRE(*pOfferSrc == *pOfferDst);
        BOOST_REQUIRE(pMatchDst != nullptr);
        BOOST_REQUIRE(*pMatchSrc == *pMatchDst);
    }

    BOOST_AUTO_TEST_CASE(CheckVectorSerialization){
        std::string str;
        std::vector<std::unique_ptr<TransactionDTO>> src_tx, dst_tx;
        src_tx.emplace_back(std::make_unique<TransactionDTO>(10));
        src_tx.emplace_back(std::make_unique<OfferDTO>(10, 1.1));
        src_tx.emplace_back(std::make_unique<MatchDTO>(10, false));
        {
            std::ostringstream ofs;
            boost::archive::binary_oarchive oa(ofs);
            oa << src_tx;
            str = ofs.str();
        }
        {
            std::istringstream ifs(str);
            boost::archive::binary_iarchive ia(ifs);
            ia >> dst_tx;
        }
        BOOST_REQUIRE_EQUAL(src_tx.size(), dst_tx.size());
        for(auto i=0; i < dst_tx.size(); ++i){
            BOOST_REQUIRE(*src_tx[i] == *dst_tx[i]);
        }
    }

BOOST_AUTO_TEST_SUITE_END()
