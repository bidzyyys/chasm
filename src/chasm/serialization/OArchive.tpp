//
// Created by Piotr Żelazko on 15/11/2018.
//

#ifndef CHASM_OARCHIVE_TPP
#define CHASM_OARCHIVE_TPP

namespace chasm::serialization {


    template<>
    struct OArchive::Worker<std::byte, void> {
        OArchive &operator()(OArchive &archive, std::byte const &obj) const {
            archive.bytes_->push_back(obj);
            return archive;
        }
    };

    template<typename T>
    struct OArchive::Worker<T, std::enable_if_t<std::numeric_limits<T>::is_integer>> {
        OArchive &operator()(OArchive &archive, T const &obj) const {
            T integer = obj;
            for (auto i = 0; i < sizeof(T); ++i) {
                integer >>= (8 * i);
                archive.bytes_->push_back(std::byte(integer & 0xff));
            }
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
