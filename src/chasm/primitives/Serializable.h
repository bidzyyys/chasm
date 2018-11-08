//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_SERIALIZABLE_H
#define CHASM_SERIALIZABLE_H

#include <memory>
#include <any>

namespace chasm::primitives {

    struct DTO {
        //TODO: change return type
        virtual std::any acceptSerializator() = 0;

        virtual ~DTO() = 0;
    };

    class Serializable {
    public:
        virtual std::unique_ptr<DTO> toDTO() = 0;

        virtual ~Serializable() = default;
    };

}

#endif //CHASM_SERIALIZABLE_H
