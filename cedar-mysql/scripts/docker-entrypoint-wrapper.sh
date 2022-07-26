#!/bin/bash

echo "CEDAR: exporting variables ..."
export MYSQL_ROOT_PASSWORD="${CEDAR_MYSQL_ROOT_PASSWORD}"
#export MYSQL_ROOT_HOST="${CEDAR_NET_GATEWAY}"
#export MYSQL_ROOT_HOST="192.168.17.%" #"${CEDAR_NET_GATEWAY}"
export MYSQL_ROOT_HOST="%" #"${CEDAR_NET_GATEWAY}"

env

echo "CEDAR: changing owner of logs ..."
chown -R mysql:mysql "/var/log/mysql"

echo "CEDAR: executing original entrypoint:" "$@"
exec /entrypoint.sh "$@"
