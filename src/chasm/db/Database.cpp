//
// Created by Daniel Bigos on 24.11.18.
//

#include "Database.h"

using namespace chasm::db;

void Database::open() {

    leveldb::DB* db;

    leveldb::Options options;
    options.create_if_missing = true;
    leveldb::Status status = leveldb::DB::Open(options, "./testdb", &db);

}
