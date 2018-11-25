//
// Created by Daniel Bigos on 11.11.18.
//

#include "Output.hpp"

using namespace chasm;
using namespace chasm::primitives::transaction;

/// Output

Output::Output(value_t value) : value_(value) {}

value_t Output::getValue() const {
    return value_;
}

Output::~Output() {

}

/// SimpleOutput

SimpleOutput::SimpleOutput(value_t value, const address_t &receiver) : Output(value), receiver_(receiver) {}

const address_t &SimpleOutput::getReceiver() const {
    return receiver_;
}


