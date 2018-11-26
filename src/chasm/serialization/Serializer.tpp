//
// Created by Piotr Żelazko on 26/11/2018.
//

#include <chasm/primitives/Transaction.hpp>

namespace chasm::serialization {

    template <typename Ar, typename T>
    void Serializer::transform(Ar &archive, T &obj, is_root_t) {
//        archive & static_cast<std::byte>(class_id_trait<T>::value);
        Worker<Ar, T>().transform_fields(archive, obj); //TODO: make static
    }

    /// BLOCK

    /// TRANSACTIONS
    template<typename Ar>
    struct Serializer::Worker<Ar, primitives::Transaction> {
        void transform_fields(Ar &archive, primitives::Transaction &obj) {
//            archive & obj.inputs_ & obj.outputs_;
        }
    };

    /// INPUTS & OUTPUTS


    /// OTHERS
}



//
///// WORKERS
//template<typename Ar>
//struct Serializer::Worker<Ar, primitives::Block> {
//    void serialize_fields(Ar &archive, primitives::Block const &obj) {
//
//        archive & obj.header_.prevBlockHash
//        & obj.header_.merkleTreeRoot_
//        & obj.header_.timestamp_
//        & obj.header_.nonce_
//        & obj.header_.difficulty_;
//        //TODO
////            & obj.transactions_;
//    }
//};
//
//template<typename Ar>
//struct Serializer::Worker<Ar, primitives::Transaction> {
//    void serialize_fields(Ar &archive, primitives::Transaction const &obj) {
//        archive & obj.inputs_ & obj.outputs_;
//    }
//};
//
//template<typename Ar>
//struct Serializer::Worker<Ar, primitives::transaction::Input> {
//    void serialize_fields(Ar &archive, primitives::transaction::Input const &obj) {
//        archive & obj.getUTXO().getTxHash() & obj.getUTXO().getIndex();
//    }
//};
//
//template<typename Ar>
//struct Serializer::Worker<Ar, primitives::transaction::Output> {
//    void serialize_fields(Ar &archive, primitives::transaction::Output const &obj) {
//        archive & obj.getValue();
//    }
//};
//
//template<typename Ar>
//struct Serializer::Worker<Ar, primitives::transaction::SimpleOutput> {
//    void serialize_fields(Ar &archive, primitives::transaction::SimpleOutput const &obj) {
//        archive & obj.getReceiver();
//    }
//};