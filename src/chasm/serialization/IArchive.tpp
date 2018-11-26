//
// Created by Piotr Żelazko on 25/11/2018.
//
namespace chasm::serialization {
/// PARTIAL SPECIALIZATIONS
    template<typename T>
    struct Serializer::IArchive::Worker<std::vector<T>, void> {
        Serializer::IArchive &operator()(Serializer::IArchive &archive, std::vector<T> &obj) const {
            x_size_t size = 0;
            archive >> size;
            for (x_size_t i = 0; i < size; ++i) {
                T elem;
                archive >> elem;
                obj.emplace_back(std::move(elem));
            }
            return archive;
        }
    };


    template<typename T>
    struct Serializer::IArchive::Worker<T, std::enable_if_t<std::numeric_limits<T>::is_integer>> {
        Serializer::IArchive &operator()(Serializer::IArchive &archive, T &obj) const {
            obj = 0;
            for (auto i = 0; i < sizeof(T); ++i) {
                obj += static_cast<uint64_t>(*archive.current_) << 8 * i;
                ++archive.current_;
            }
            return archive;
        }
    };

    template<typename T>
    struct Serializer::IArchive::Worker<std::unique_ptr<T>, void> {
        Serializer::IArchive &operator()(Serializer::IArchive &archive, std::unique_ptr<T> &obj) const {
            obj = std::make_unique<T>();
            archive >> *obj;
            return archive;
        }
    };

/// SPECIALIZATIONS
    template<>
    struct Serializer::IArchive::Worker<hash_t, void> {
        Serializer::IArchive &operator()(Serializer::IArchive &archive, hash_t &obj) const {
            for (x_size_t i = 0; i < obj.size(); ++i, ++archive.current_) obj.at(i) = *archive.current_;
            return archive;
        }
    };

    template<>
    struct Serializer::IArchive::Worker<std::byte, void> {
        Serializer::IArchive &operator()(Serializer::IArchive &archive, std::byte &obj) const {
            obj = *archive.current_;
            ++archive.current_;
            return archive;
        }
    };

//    template<>
//    struct Serializer::IArchive::Worker<const class_id, void> {
//        Serializer::IArchive &operator()(Serializer::IArchive &archive, class_id  const& obj) const {
////            archive.buffer_.push_back(static_cast<std::byte>(obj));
//            return archive;
//        }
//    };
}