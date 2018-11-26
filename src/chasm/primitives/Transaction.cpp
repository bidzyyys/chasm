//
// Created by Daniel Bigos on 11.11.18.
//

#include <chasm/serialization/Serializer.hpp>
#include "Transaction.hpp"

using namespace chasm;
using namespace chasm::primitives;

void Transaction::addInput(hash_t const &txHash, in_idx_t input) {
    if (inputs_.size() > std::numeric_limits<x_size_t>::max()) throw std::length_error("Too many inputs");
    inputs_.push_back(std::make_unique<transaction::Input>(txHash, input));
}

void Transaction::addInput(hash_t &&txHash, in_idx_t input) {
    if (inputs_.size() > std::numeric_limits<x_size_t>::max()) throw std::length_error("Too many inputs");
    inputs_.push_back(std::make_unique<transaction::Input>(txHash, input));
}

void Transaction::addOutput(value_t value, address_t const &receiver) {
    if (outputs_.size() > std::numeric_limits<x_size_t>::max()) throw std::length_error("Too many outputs");
    outputs_.push_back(std::make_unique<transaction::SimpleOutput>(value, receiver));;
}



const transaction::Input &Transaction::getInput(x_size_t index) const {
    return *inputs_.at(index);
}

const transaction::Output &Transaction::getOutput(x_size_t index) const {
    return *outputs_.at(index);
}

//void Transaction::accept(serialization::Serializer &serializer) {
//    serializer.visit(*this);
//}
