#!/bin/bash
set -m

$MONGO_SCRIPTS_DIR/mongo_setup_users.sh

$MONGO_SCRIPTS_DIR/mongo_create_cedar_objects.sh

cmd="gosu mongodb mongod --storageEngine $MONGO_STORAGE_ENGINE --keyFile $MONGO_KEYFILE"

if [ "$MONGO_AUTH" == true ]; then
  cmd="$cmd --auth"
fi

if [ "$MONGO_JOURNALING" == false ]; then
  cmd="$cmd --nojournal"
fi

if [[ "$MONGO_OPLOG_SIZE" ]]; then
  cmd="$cmd --oplogSize $OPLOG_SIZE"
fi

if [ ! -d "$MONGO_DB_PATH" ]; then
  mkdir -p $MONGO_DB_PATH
fi

mkdir -p $MONGO_LOG_PATH

cmd="$cmd --logpath $MONGO_LOG_PATH/mongo.log"

chown -R mongodb:mongodb $MONGO_DB_PATH

$cmd --dbpath $MONGO_DB_PATH &

fg