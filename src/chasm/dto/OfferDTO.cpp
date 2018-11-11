//
// Created by Daniel Bigos on 08.11.18.
//

#include "OfferDTO.h"

using namespace chasm;
using namespace dto;

OfferDTO::OfferDTO(int value, double amount) :
 TransactionDTO(value), amount_(amount) {}

double OfferDTO::amount() const {
    return amount_;
}

bool OfferDTO::operator==(const TransactionDTO &rh) const {
    const auto *pRH = dynamic_cast<const OfferDTO*>(&rh);
    return pRH != nullptr && pRH->amount_ == this->amount_;
}

OfferDTO::OfferDTO() :
    amount_(0.0) {}

