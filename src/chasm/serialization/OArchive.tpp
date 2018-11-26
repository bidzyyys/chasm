//
// Created by Piotr Żelazko on 26/11/2018.
//

namespace chasm::serialization {

    template<typename T, typename Enabled>
    Serializer::OArchive &Serializer::OArchive::Worker<T, Enabled>::operator()(
            chasm::serialization::Serializer::OArchive &archive, T &obj) {
//        obj.accept(archive.serializer_);
          archive.serializer_.visit(obj);
//        archive.serializer_.transform(archive, obj, inheritance_trait_t<T>());
        return archive;
    }

/// PARTIAL SPECIALIZATIONS
    template<typename T>
    struct Serializer::OArchive::Worker<std::vector<T>, void> {
        Serializer::OArchive &operator()(Serializer::OArchive &archive, std::vector<T> &obj) const {
            auto size = static_cast<x_size_t>(obj.size());
            archive << size;
            for (T const &elem : obj) archive << elem;
            return archive;
        }
    };

    template<typename T>
    struct Serializer::OArchive::Worker<std::unique_ptr<T>, void> {
        Serializer::OArchive &operator()(Serializer::OArchive &archive, std::unique_ptr<T> &obj) const {
            archive << *obj;
            return archive;
        }
    };

    template<typename T>
    struct Serializer::OArchive::Worker<T, std::enable_if_t<std::numeric_limits<T>::is_integer>> {
        Serializer::OArchive &operator()(Serializer::OArchive &archive, T &obj) const {
            for (auto i = 0; i < sizeof(T); ++i)
                archive.buffer_.push_back(std::byte((obj >> i * 8) & 0xff));
            return archive;
        }
    };

/// SPECIALIZATIONS
    template<>
    struct Serializer::OArchive::Worker<hash_t, void> {
        Serializer::OArchive &operator()(Serializer::OArchive &archive, hash_t const &obj) const {
            archive.buffer_.insert(archive.buffer_.end(), obj.begin(), obj.end());
            return archive;
        }
    };

    template<>
    struct Serializer::OArchive::Worker<std::byte, void> {
        Serializer::OArchive &operator()(Serializer::OArchive &archive, std::byte &obj) const {
            archive.buffer_.push_back(obj);
            return archive;
        }
    };

//    template<>
//    struct Serializer::OArchive::Worker<const class_id, void> {
//        Serializer::OArchive &operator()(Serializer::OArchive &archive, class_id  const& obj) const {
//            archive.buffer_.push_back(static_cast<std::byte>(obj));
//            return archive;
//        }
//    };
}