//
// Created by Daniel Bigos on 08.11.18.
//

#include "TransactionDTO.h"

using namespace chasm::dto;

TransactionDTO::TransactionDTO(int value) :
    value_(value) {}

int TransactionDTO::value() const {
    return value_;
}

bool TransactionDTO::operator==(const TransactionDTO &rh) const {
    return this->value_ == rh.value_;
}

TransactionDTO::TransactionDTO() :
    value_(0) {}
