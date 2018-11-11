//
// Created by Daniel Bigos on 08.11.18.
//

#ifndef CHASM_OFFERDTO_H
#define CHASM_OFFERDTO_H

#include "TransactionDTO.h"

namespace chasm{
    namespace dto{
        class OfferDTO;
    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::OfferDTO &dto, unsigned int version);
    }
}

namespace chasm {
    namespace dto {
        class OfferDTO : public TransactionDTO {
        public:
            OfferDTO();

            OfferDTO(int value, double amount);

            ~OfferDTO() override = default;

            double amount() const;

            bool operator==(const TransactionDTO &rh) const override;

        private:
            friend class boost::serialization::access;

            template<typename Archive>
            friend void boost::serialization::serialize(Archive &ar, OfferDTO &dto, unsigned int version);

            double amount_;
        };
    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::OfferDTO &dto, unsigned int version){
            ar & boost::serialization::base_object<chasm::dto::TransactionDTO>(dto);
            ar & dto.amount_;
        }
    }
}

#endif //CHASM_OFFERDTO_H
