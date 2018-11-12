//
// Created by Piotr Żelazko on 11/11/2018.
//

#ifndef CHASM_SERIALIZABLE_H
#define CHASM_SERIALIZABLE_H

#include <memory>
#include <any>
#include <boost/serialization/unique_ptr.hpp>
#include <boost/serialization/assume_abstract.hpp>
#include <boost/serialization/export.hpp>
#include <vector>

namespace chasm::primitives{
    class Serializable;
}

namespace boost::serialization{
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::Serializable &obj, unsigned int version);
}

namespace chasm::primitives {
    class Serializable {
    public:
        //TODO: change return type
        //        virtual std::any acceptSerializator() = 0;

        virtual ~Serializable() = 0;

        std::vector<std::byte> toByteArray();

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, Serializable &obj,
                                                    unsigned int version);
    };
}

namespace boost::serialization{
    template <typename Archive>
    void serialize(Archive &ar, chasm::primitives::Serializable &obj,
            unsigned int version){
    }
}

BOOST_SERIALIZATION_ASSUME_ABSTRACT(chasm::primitives::Serializable)

#endif //CHASM_SERIALIZABLE_H
