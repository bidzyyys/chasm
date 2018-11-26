//
// Created by Daniel Bigos on 24.11.18.
//

#ifndef CHASM_DATABASE_H
#define CHASM_DATABASE_H

#include <leveldb/db.h>
#include <stdexcept>
#include <optional>
#include <functional>
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
        DatabaseError(const std::string &error_message);
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
         * Create database if does not exist
         * @param database_name
         * @throws DatabaseError if an error occurs
         */
        void open(const std::string &database_name);

        /**
         * Insert record into database
         * In case of opened connection, the previous one is closed
         * @param key
         * @param value
         * @throws DatabaseError if an error occurs
         */
        void insertRecord(const chasm::types::hash_t &key, const chasm::types::bytes_t &value) const;

        /**
         * Select record from database
         * @param key
         * @return chasm::types::bytes_t or std::nullopt_t if record with given key does not exist
         * @throws DatabaseError if an error occurs
         */
        std::optional<chasm::types::bytes_t> selectRecord(const chasm::types::hash_t &key) const;

        /**
         * Delete record from database
         * @param key
         * @throws DatabaseError if an error occurs
         */
        void deleteRecord(const chasm::types::hash_t &key) const;

        /**
         * Close database connection
         */
        void close();

    private:
        using db_t = std::unique_ptr<leveldb::DB, std::function<void(leveldb::DB* db)>>;

        static void closeConnection(leveldb::DB *db);

        void cleanConnection();

        db_t database;
    };
}

#endif //CHASM_DATABASE_H
