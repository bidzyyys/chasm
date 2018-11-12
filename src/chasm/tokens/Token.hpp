//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_TOKENS_HPP
#define CHASM_TOKENS_HPP

#include <memory>
#include <vector>
#include <cstddef>

#include <boost/optional.hpp>

#include <chasm/types.hpp>

namespace chasm::tokens {

    class Token {
    public:
        enum class Tokens : uint16_t {
            XPEER_COIN
        };

        static const Token &getToken(Tokens);

        class TransactionInclusionProof {
        public:

            virtual bool acceptInclusionValidator() = 0; //TODO: Rename result into validation result

            virtual ~TransactionInclusionProof() = default;

        };

        class Address {
        public:
            virtual ~Address() = 0;
        };

        virtual boost::optional<uptr_t<TransactionInclusionProof>> buildProof(types::bytes_t const&) const = 0; //TODO: strong types

        virtual boost::optional<uptr_t<Address>> buildAddress(types::bytes_t const &) const = 0;

        virtual ~Token() = default;
    };

}

namespace chasm::types {
    using token_t = chasm::tokens::Token::Tokens;
    using proof_t = chasm::tokens::Token::TransactionInclusionProof;
}


#endif //CHASM_TOKENS_HPP
