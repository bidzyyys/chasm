//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_OFFER_TRANSACTION_H
#define CHASM_OFFER_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>
#include <chasm/common/supported_tokens/Token.hpp>

namespace chasm::primitives::transaction{
    class OfferTransaction;
}

namespace boost::serialization{
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::OfferTransaction &tx,
                   unsigned int version);
}

namespace chasm::primitives::transaction {

    /*!
     * \brief Transaction of offer type
     *
     * This type of a transaction can be used to make an offer.
     * Both tokens with values must be specified.
     *
     * \b Note: offer must have an unique hash as it is later the identifier of the whole exchange.
     * Use \i nonce field to adjust the hash.
     */
    class OfferTransaction : public Transaction {
    public:

        ~OfferTransaction() override = default;

        bool operator==(const OfferTransaction &rh) const;

    private:
        friend class boost::serialization::access;

        template<typename Archive>
        friend void boost::serialization::serialize(Archive &ar, OfferTransaction &tx,
                       unsigned int version);

        using nonce_t = uint16_t;

        common::types::token_t tokenIn_; //!< Token being offered
        common::types::value_t valueIn_; //!< Value being offered

        common::types::token_t tokenOut_; //!< Token being demanded
        common::types::value_t valueOut_; //!< Value being demanded

        common::types::address_t address_; //!< Receiver's address (on the blockchain where the exchange happens)

        //! Time in seconds how long will the offer be 'matchable',
        //! starting from the timestamp of the block in which the transaction was included in.
        common::types::timestamp_t offerTimeout_;
        nonce_t nonce_; //!< used to adjust a hash of an offer. \b Note: it is not of the same type as \ref Block::nonce_t

        common::types::out_idx_t confirmationFeeIndex_; //!< Index of confirmation fee. The output must be of type \b FeeOutput
        common::types::out_idx_t bailIndex_; //!< Index of bail
    };

}

namespace boost::serialization {
    template<typename Archive>
    void serialize(Archive &ar, chasm::primitives::transaction::OfferTransaction &tx,
                   unsigned int version){
        ar & boost::serialization::base_object<chasm::primitives::Transaction>(tx);
        ar & tx.tokenIn_;
        ar & tx.valueIn_;
        ar & tx.tokenOut_;
        ar & tx.valueOut_;
        ar & tx.address_;
        ar & tx.offerTimeout_;
        ar & tx.nonce_;
        ar & tx.confirmationFeeIndex_;
        ar & tx.bailIndex_;
    }
}

#endif //CHASM_OFFER_TRANSACTION_H
