//
// Created by Daniel Bigos on 08.11.18.
//

#ifndef CHASM_TRANSACTIONDTO_H
#define CHASM_TRANSACTIONDTO_H

#include <boost/serialization/unique_ptr.hpp>

namespace chasm{
    namespace dto{
        class TransactionDTO;
    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::TransactionDTO &dto, unsigned int version);
    }
}

namespace chasm {
    namespace dto {
        class TransactionDTO {

        public:
            TransactionDTO();

            explicit TransactionDTO(int value);

            virtual ~TransactionDTO() = default;

            virtual bool operator==(const TransactionDTO &rh) const;

            int value() const;

        private:
            friend class boost::serialization::access;

            template<typename Archive>
            friend void boost::serialization::serialize(Archive &ar, TransactionDTO &dto, unsigned int version);

            int value_;
        };
    }
}

namespace boost{
    namespace serialization{
        template<typename Archive>
        void serialize(Archive &ar, chasm::dto::TransactionDTO &dto, unsigned int version){
            ar & dto.value_;
        }
    }
}

#endif //CHASM_TRANSACTIONDTO_H
