//
// Created by Piotr Żelazko on 25/11/2018.
//

#ifndef CHASM_ALT_SERIALIZER_HPP
#define CHASM_ALT_SERIALIZER_HPP

#include <variant>
#include <optional>
#include <chasm/types.hpp>

#include "traits.hpp"


namespace chasm::serialization {
    using namespace chasm;
    using namespace traits::classes;
    using namespace traits::inheritance;

    class Serializer {
    public:
        template<typename T>
        bytes_t serialize(T& obj) {
            archive_.emplace<1>(*this);
            std::get<1>(archive_) << obj;
            return std::get<1>(archive_).resetBuffer();
        }

        template<typename T>
        bytes_t serialize(T const& obj) {
            return serialize(const_cast<T&>(obj));
        }

        template<typename T>
        T deserialize(bytes_t const &buffer) {
            archive_.emplace<2>(*this, buffer.cbegin());
            T obj;
            std::get<2>(archive_) >> obj;
            return std::move(obj);
        }

        template<typename T>
        void visit(T &obj) {
            std::visit(overloaded{
                    [& obj, this](IArchive &archive) {
                        transform(archive, obj, inheritance_trait_t<T>());
                    },
                    [& obj, this](OArchive &archive) {
                        transform(archive, obj, inheritance_trait_t<T>());
                    },
                    [](std::monostate&){
                        throw std::runtime_error("Serializer must be initialised first. User either serialize or deserialize methods");
                    }
            }, archive_);
        }

    private:

        template<class... Ts>
        struct overloaded : Ts ... {
            using Ts::operator()...;
        };
        template<class... Ts> overloaded(Ts...) -> overloaded<Ts...>;

        class OArchive {
        public:

            OArchive(Serializer &serializer) : serializer_(serializer) {}

            template<typename T>
            OArchive &operator&(T &obj) {
                return operator<<(obj);
            }

            template<typename T>
            OArchive &operator<<(T &obj) {
                return Worker<T>()(*this, obj);
            }

            bytes_t resetBuffer() {
                return buffer_;
            }

            virtual ~OArchive() = default;

        private:
            template<typename T, typename Enabled = void>
            struct Worker {
                OArchive &operator()(OArchive &archive, T &obj);
            };

            Serializer &serializer_;
            bytes_t buffer_;
        };

        class IArchive {
        public:
            IArchive(Serializer &serializer, const bytes_t::const_iterator begin) : serializer_(serializer),
                                                                                    current_(begin) {}

            template<typename T>
            IArchive &operator&(T &obj) {
                return operator>>(obj);
            }

            template<typename T>
            IArchive &operator>>(T &obj) {
                return Worker<T>()(*this, obj);
            }

            virtual ~IArchive() = default;

        private:
            template<typename T, typename Enabled = void>
            struct Worker {
                IArchive &operator()(IArchive &archive, T &obj);
            };

            Serializer &serializer_;
            bytes_t::const_iterator current_;
        };

        template<typename Ar, typename T>
        class Worker {
            void transform_fields(Ar &archive, T &obj);
        };

        template <typename Ar, typename T>
        void transform(Ar &archive, T &obj, is_root_t);

//        template <typename Ar, typename T, typename B>
//        void transform(Ar &archive, T &obj, is_derived_t<B>) {
////            archive & class_id_trait<T>::value;
//            Worker<Ar, B>().transform(archive, static_cast<B &>(obj, inheritance_trait_t<T>())); //TODO: make static
//            Worker<Ar, T>().transform_fields(archive, obj); //TODO: make static
//        }

        std::variant<std::monostate, OArchive, IArchive> archive_;

    };
}

#include "Serializer.tpp"
#include "IArchive.tpp"
#include "OArchive.tpp"

#endif //CHASM_ALT_SERIALIZER_HPP
