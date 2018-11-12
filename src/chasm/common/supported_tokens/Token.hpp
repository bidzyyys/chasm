//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_TOKENS_HPP
#define CHASM_TOKENS_HPP

#include <memory>

namespace chasm::common::tokens{

    class Token {
    public:
        enum class Tokens: uint16_t {
            XPEER_COIN
        };

        static const Token& getToken(Tokens);

        class TransactionInclusionProof {
        public:

            virtual bool acceptInclusionValidator() = 0;

            virtual ~TransactionInclusionProof() = default;

        };

        virtual std::unique_ptr<TransactionInclusionProof> buildProof(const std::vector<std::byte>&) const = 0;

    };

}


#endif //CHASM_TOKENS_HPP
