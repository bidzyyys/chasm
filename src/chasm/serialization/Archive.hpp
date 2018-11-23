//
// Created by Piotr Żelazko on 15/11/2018.
//

#ifndef CHASM_ARCHIVE_HPP
#define CHASM_ARCHIVE_HPP

#include <memory>
#include <chasm/types.hpp>

namespace chasm::serialization{
    class Serializer;

    class Archive {
    public:
        Archive() = default;

        bool isBufferEmpty() {
            return !bytes_ || bytes_->empty();
        }

        bytes_t getBuffer() {
            bytes_->shrink_to_fit();
            return *bytes_;
        }

        virtual ~Archive() = default;

    protected:
        std::unique_ptr<bytes_t> bytes_;
    };

    class OArchive : public Archive {
    public:
        explicit OArchive() : Archive() {
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

        ~OArchive() override = default;

    private:
        template<typename T, typename Enabled = void>
        struct Worker {
            OArchive &operator()(OArchive & archive, T const &obj) const;
        };

    };
}

#include "OArchive.tpp"

#endif //CHASM_ARCHIVE_HPP
