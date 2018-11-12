//
// Created by Piotr Żelazko on 12/11/2018.
//

#include <map>
#include "Token.hpp"
#include "XpeerCoinToken.hpp"

using namespace chasm::tokens;

const Token &Token::getToken(Tokens token) {
    static auto tokens = [tokens = std::map<Tokens, std::unique_ptr<Token>>{}]() mutable {

        tokens.emplace(Tokens::XPEER_COIN, std::make_unique<XpeerCoinToken>());

        return std::move(tokens);
    }();

//    return *tokens.at(token);

    return *(new XpeerCoinToken());
}
