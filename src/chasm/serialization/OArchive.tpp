//
// Created by Piotr Żelazko on 15/11/2018.
//

#ifndef CHASM_OARCHIVE_TPP
#define CHASM_OARCHIVE_TPP

namespace chasm::serialization {


    template<typename T, typename Enabled>
    OArchive &OArchive::Worker<T, Enabled>::operator()(OArchive &archive, T const &obj) const {
        Serializer::acceptReturn(archive, obj);
        return archive;
    }

    /// PARTIAL SPECIALIZATIONS
    template<typename T>
    struct OArchive::Worker<std::vector<T>, void> {
        OArchive &operator()(OArchive &archive, std::vector<T> const &obj) const {
            archive << static_cast<uint16_t >(obj.size());
            for (T const &elem : obj) archive << elem;
            return archive;
        }
    };

    template<typename T>
    struct OArchive::Worker<std::unique_ptr<T>, void> {
        OArchive &operator()(OArchive &archive, std::unique_ptr<T> const &obj) const {
            archive << *obj;
            return archive;
        }
    };

    template<typename T>
    struct OArchive::Worker<T, std::enable_if_t<std::numeric_limits<T>::is_integer>> {
        OArchive &operator()(OArchive &archive, T const &obj) const {
            for (auto i = 0; i < sizeof(T); ++i)
                archive.bytes_->push_back(std::byte((obj >> i * 8) & 0xff));

            return archive;
        }
    };

    /// SPECIALIZATIONS
    template<>
    struct OArchive::Worker<std::byte, void> {
        OArchive &operator()(OArchive &archive, std::byte const &obj) const {
            archive.bytes_->push_back(obj);
            return archive;
        }
    };

    template<>
    struct OArchive::Worker<hash_t, void> {
        OArchive &operator()(OArchive &archive, hash_t const &obj) const {
            archive.bytes_->insert(archive.bytes_->end(), obj.begin(), obj.end());
            return archive;
        }
    };

}


#endif //CHASM_OARCHIVE_TPP
