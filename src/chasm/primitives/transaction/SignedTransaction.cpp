//
// Created by Daniel Bigos on 12.11.18.
//

#include "SignedTransaction.hpp"

using namespace chasm::primitives::transaction;

bool SignedTransaction::operator==(const SignedTransaction &rh) const {
    return *transaction_ == *rh.transaction_ &&
            std::equal(signatures_.begin(), signatures_.end(), rh.signatures_.begin(),
                       [](const std::unique_ptr<common::types::signature_t> & l,
                          const std::unique_ptr<common::types::signature_t> & r) {
                           return (*l == *r);});
}