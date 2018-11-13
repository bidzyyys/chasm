//
// Created by Daniel Bigos on 11.11.18.
//

#include "Output.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

bool Output::operator==(const Output &rh) const {
    return value_ == rh.value_;
}

bool FeeOutput::operator==(const FeeOutput &rh) const {
    return Output::operator==(rh) &&
           compare_collection(offerHash_, rh.offerHash_);
}

bool SimpleOutput::operator==(const SimpleOutput &rh) const {
    return Output::operator==(rh) &&
           compare_collection(receiver_, rh.receiver_);
}

