//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_SERIALIZABLE_H
#define CHASM_SERIALIZABLE_H

#include <memory>
#include <any>

namespace chasm::primitives {

    class Serializable {
    public:
        //TODO: change return type
        virtual std::any acceptSerializator() = 0;

        virtual ~Serializable() = 0;
    };

}

#endif //CHASM_SERIALIZABLE_H
