//
// Created by Daniel Bigos on 24.11.18.
//

#include "Database.hpp"

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

    auto status = leveldb::DB::Open(options, database_name, &db);

    if (!status.ok() || db == nullptr) {
        throw DatabaseError("Unexpected error while opening connection: " + status.ToString());
    }

    database = db_t(db);
}

void Database::insertRecord(const hash_t &key, const bytes_t &value) const {

    if (!isOpened()) {
        throw DatabaseError("Connection is not opened");
    }

    leveldb::WriteBatch batch;
    batch.Delete(toString(key));
    batch.Put(toString(key), toString(value));

    leveldb::WriteOptions options;
    options.sync = true;

    auto status = database->Write(options, &batch);

    if (!status.ok()) {
        throw DatabaseError("Unexpected error while inserting into database: " + status.ToString());
    }
}

std::optional<bytes_t> Database::selectRecord(const hash_t &key) const {

    if (!isOpened()) {
        throw DatabaseError("Connection is not opened");
    }

    std::string value;
    std::optional<bytes_t> result;

    auto status = database->Get(leveldb::ReadOptions(), toString(key), &value);

    if (status.ok()) {
        result = std::make_optional(toBytes(value));
    }
    else if (status.IsNotFound()) {
        result = std::nullopt;
    }
    else {
        throw DatabaseError("Unexpected error while selecting from database: " + status.ToString());
    }

    return result;
}

void Database::deleteRecord(const hash_t &key) const {

    if (!isOpened()) {
        throw DatabaseError("Connection is not opened");
    }

    leveldb::WriteBatch batch;
    batch.Delete(toString(key));

    leveldb::WriteOptions options;
    options.sync = true;

    auto status = database->Write(options, &batch);

    if (!status.ok()) {
        throw DatabaseError("Unexpected error while deleting from database: " + status.ToString());
    }
}

Database::Database() {

    cleanConnection();
}

void Database::close() {

    cleanConnection();
}

void Database::cleanConnection() {

    database = nullptr;
}

bool Database::isOpened() const{

    return database != nullptr;
}



