//
// Created by Daniel Bigos on 08.11.18.
//

#ifndef CHASM_ACCEPTANCEDTO_H
#define CHASM_ACCEPTANCEDTO_H

#include "TransactionDTO.h"

namespace chasm{
    namespace dto{
        class MatchDTO;
    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::MatchDTO &dto, unsigned int version);
    }
}

namespace chasm {
    namespace dto {
        class MatchDTO : public TransactionDTO {
        public:
            MatchDTO();

            MatchDTO(int value, bool flag);

            ~MatchDTO() override = default;

            bool flag() const;

            bool operator==(const TransactionDTO &rh) const override;

        private:
            friend class boost::serialization::access;

            template<typename Archive>
            friend void boost::serialization::serialize(Archive &ar, MatchDTO &dto, unsigned int version);

            bool flag_;
        };

    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::MatchDTO &dto, unsigned int version){
            ar & boost::serialization::base_object<chasm::dto::TransactionDTO>(dto);
            ar & dto.flag_;
        }
    }
}


#endif //CHASM_ACCEPTANCEDTO_H
