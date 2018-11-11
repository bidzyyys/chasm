//
// Created by Daniel Bigos on 08.11.18.
//

#include "MatchDTO.h"

using namespace chasm;
using namespace dto;

MatchDTO::MatchDTO() :
    flag_(true) {}

MatchDTO::MatchDTO(int value, bool flag) :
    TransactionDTO(value), flag_(flag) {}

bool MatchDTO::flag() const {
    return flag_;
}

bool MatchDTO::operator==(const TransactionDTO &rh) const {
    const auto *pRH = dynamic_cast<const MatchDTO*>(&rh);
    return pRH != nullptr && pRH->flag_ == this->flag_;
}
