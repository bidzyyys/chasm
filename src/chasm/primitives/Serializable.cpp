//
// Created by Daniel Bigos on 11.11.18.
//

#include <boost/archive/binary_oarchive.hpp>
#include <sstream>
#include "chasm/primitives/Serializable.h"
#include "Serializable.h"


using namespace chasm::primitives;

std::vector<std::byte> Serializable::toByteArray() {
    std::ostringstream ofs;
    boost::archive::binary_oarchive oa(ofs);
    oa << *this;
    auto str = ofs.str();
    std::vector<std::byte> bytes;
    std::transform(str.begin(), str.end(),
            std::back_inserter(bytes),
            [](const unsigned char c){
        return static_cast<std::byte>(c);
    });
    return bytes;
}
