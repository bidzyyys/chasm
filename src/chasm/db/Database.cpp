//
// Created by Daniel Bigos on 24.11.18.
//

#include "Database.h"

using namespace chasm::db;
using namespace chasm::types;

DatabaseError::DatabaseError(const std::string &error_message)
        : runtime_error(error_message) {}

Database::~Database() = default;

void Database::open(const std::string &database_name) {

    cleanConnection();

    leveldb::DB* db = nullptr;
    leveldb::Options options;
    options.create_if_missing = true;

    leveldb::Status status = leveldb::DB::Open(options, database_name, &db);

    if (!status.ok() || db == nullptr) {
        throw DatabaseError("Unexpected error while opening connection: " + status.ToString());
    }

    database = db_t(db, &closeConnection);
}

void Database::insertRecord(const hash_t &key, const bytes_t &value) const {

}

std::optional<bytes_t> Database::selectRecord(const hash_t &key) const {

    return std::optional<bytes_t>();
}

void Database::deleteRecord(const hash_t &key) const {

}

Database::Database() {

    cleanConnection();
}

void Database::closeConnection(leveldb::DB *db) {

    delete db;
}

void Database::close() {

    cleanConnection();
}

void Database::cleanConnection() {

    database = nullptr;
}


