//
// Created by Piotr Żelazko on 12/11/2018.
//



#include <map>
#include "Token.hpp"
#include "XpeerCoinToken.hpp"

using namespace chasm::common::tokens;

const Token& Token::getToken(Tokens token){
    static auto tokens = [tokens = std::map<int, std::unique_ptr<Token>>{}]() mutable {

        tokens.emplace(Tokens::XPEER_COIN, std::make_unique<XpeerCoinToken>());

        return std::move(tokens);
    }();

    return *tokens.at(token);
}
