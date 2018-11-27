//
// Created by Daniel Bigos on 24.11.18.
//

#ifndef CHASM_DATABASE_H
#define CHASM_DATABASE_H

#include <stdexcept>
#include <optional>
#include <functional>
#include <leveldb/db.h>
#include <leveldb/write_batch.h>
#include "chasm/types.hpp"

namespace chasm::db {

    /**
     * Database Library Exception
     * Derived from std::runtime_error
     * Thrown when unexpected error occurs
     */
    class DatabaseError : public std::runtime_error {

    public:

        /**
         * Default constructor
         * @param error_message
         */
        explicit DatabaseError(const std::string &error_message);
    };

    /**
     *  Database library
     *  Wrap LevelDB
     */
    class Database {

    public:

        /**
         * Default constructor
         */
        explicit Database();

        /**
         * Default destructor
         */
        virtual ~Database();

        /**
         * Open connection to the database
         * Create database if not exist
         * @param database_name
         * @throws DatabaseError if an error occurs
         */
        void open(const std::string &database_name);

        /**
         * Insert record into database
         * In case of opened connection, the previous one is closed
         * Synchronous operation
         * @param key
         * @param value
         * @throws DatabaseError if an error occurs
         */
        void insertRecord(const chasm::types::hash_t &key, const chasm::types::bytes_t &value) const;

        /**
         * Select record from database
         * @param key
         * @return chasm::types::bytes_t or std::nullopt if record with given key does not exist
         * @throws DatabaseError if an error occurs
         */
        std::optional<chasm::types::bytes_t> selectRecord(const chasm::types::hash_t &key) const;

        /**
         * Delete record from database
         * Synchronous operation
         * @param key
         * @throws DatabaseError if an error occurs
         */
        void deleteRecord(const chasm::types::hash_t &key) const;

        /**
         * Close database connection
         */
        void close();

    private:
        using db_t = std::unique_ptr<leveldb::DB>;

        /**
         * Replace current connection with uninitialized state(nullptr)
         */
        void cleanConnection();

        /**
         * Check whether database connection is open
         * @return true if leveldb::DB ptr is not null
         */
        bool isOpened() const;

        /**
         * Convert collection of std::byte to std::string
         * @tparam T collction of std::byte
         * @param bytes
         * @return bytes converted to std::string
         */
        template <typename T>
        static std::string toString(T const &bytes) {

            std::string data;

            std::transform(bytes.begin(), bytes.end(), std::back_inserter(data), [](const std::byte &byte){ return static_cast<char>(byte); });

            return data;
        }

        /**
         * Convert collection of uint8 to std::vector<std::byte>
         * @param data
         * @return collection of uint8 converted to bytes
         */
        template<typename T>
        static chasm::types::bytes_t toBytes(T const& data) {

            chasm::types::bytes_t bytes(data.size());

            std::transform(data.begin(), data.end(), bytes.begin(), [](const uint8_t &sign){ return static_cast<std::byte >(sign); });

            return bytes;
        }

        /**
         *  std::unique_ptr<leveldb::DB>
         *  holds connection to the database
         */
        db_t database;
    };
}

#endif //CHASM_DATABASE_H
