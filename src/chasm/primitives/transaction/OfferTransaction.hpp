//
// Created by Piotr Żelazko on 08/11/2018.
//

#ifndef CHASM_OFFER_TRANSACTION_H
#define CHASM_OFFER_TRANSACTION_H

#include <chasm/primitives/Transaction.hpp>
#include <chasm/tokens/Token.hpp>

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

        using nonce_t = uint16_t;

        token_t tokenIn_; //!< Token being offered
        value_t valueIn_; //!< Value being offered

        token_t tokenOut_; //!< Token being demanded
        value_t valueOut_; //!< Value being demanded

        address_t address_; //!< Receiver's address (on tokenOut blockchain)

        //! Time in seconds how long will the offer be 'matchable',
        //! starting from the timestamp of a block which the transaction was included in.
        timestamp_t offerTimeout_;
        nonce_t nonce_; //!< used to adjust a hash of an offer. \b Note: it is not of the same type as \ref Block::nonce_t

        out_idx_t confirmationFeeIndex_; //!< Index of confirmation fee. The output must be of type \b FeeOutput
        out_idx_t bailIndex_; //!< Index of bail
    };

}

#endif //CHASM_OFFER_TRANSACTION_H
