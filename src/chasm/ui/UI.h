//
// Created by Daniel Bigos on 24.11.18.
//

#ifndef CHASM_UI_H
#define CHASM_UI_H

#include <iostream>
#include <iomanip>

namespace chasm::ui {

        template <typename T>
        std::string bytesToHexString(T const& bytes) {

            std::stringstream ss;

            for(const auto &byte: bytes) {
                ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
            }

            return ss.str();
        }
}

#endif //CHASM_UI_H
