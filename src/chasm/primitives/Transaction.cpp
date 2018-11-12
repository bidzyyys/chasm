//
// Created by Daniel Bigos on 11.11.18.
//

#include "Transaction.hpp"

using namespace chasm::primitives;

bool Transaction::operator==(const Transaction &rh) const {
    return std::equal(inputs_.begin(), inputs_.end(), rh.inputs_.begin(),
            [](const std::unique_ptr<transaction::Input> & l,
                    const std::unique_ptr<transaction::Input> & r) {
                    return (*l == *r);}) &&
        std::equal(outputs_.begin(), outputs_.end(), rh.outputs_.begin(),
                [](const std::unique_ptr<transaction::Output> & l,
                        const std::unique_ptr<transaction::Output> & r) {
                        return (*l == *r);});
}