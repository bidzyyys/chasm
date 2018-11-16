//
// Created by Piotr Żelazko on 15/11/2018.
//

#ifndef CHASM_ARCHIVE_HPP
#define CHASM_ARCHIVE_HPP

#include <type_traits>
#include <vector>
#include <chasm/types.hpp>

namespace chasm::serialization {

    class Serializer;

    class Archive {
    public:
        explicit Archive(Serializer &serializer) : serializer_(serializer) {}

        bool isBufferEmpty() {
            return !bytes_ || bytes_->empty();
        }

        bytes_t getBuffer() {
            bytes_->shrink_to_fit();
            return *bytes_;
        }

    protected:
        std::unique_ptr<bytes_t> bytes_;
        Serializer &serializer_;
    };

    class OArchive : public Archive {
    public:
        explicit OArchive(Serializer &serializer) : Archive(serializer) {
            bytes_ = std::make_unique<bytes_t>();
            bytes_->reserve(1024);
        }


        template<typename T>
        OArchive &operator<<(T const &obj) {
            return Worker<T>()(*this, obj);
        }


        template<typename T>
        OArchive &operator&(T const &obj) {
            return operator<<(obj);
        }

    private:
        template<typename T, typename Enabled = void>
        struct Worker {
            OArchive &operator()(OArchive &, T const &obj) const;
        };

    };


    class IArchive : Archive {
    public:

//        IArchive(bytes_t &&buffer);
//
//        IArchive(OArchive &&archive);
//
//        IArchive(IArchive &&archive);
//
//        template<typename T>
//        void operator>>(T &);
//
//        template<typename T,
//                typename = std::enable_if_t<std::is_class_v<T>>
//        >
//        void operator>>(T const &obj) {
//            serializer_.serialize(obj);
//        }
//
//        template<typename T>
//        void operator&(T &obj) {
//            operator>>(obj);
//        }
    };

}

#include "OArchive.tpp"

#endif //CHASM_ARCHIVE_HPP
