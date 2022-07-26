#!/bin/bash

set -e

printf "\n[-] Installing base OS dependencies...\n\n"

# base
apt-get update
apt-get install -y --no-install-recommends ca-certificates openssl numactl wget curl


# Gosu
# https://github.com/tianon/gosu
dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"
printf "\n[-] Downloading gosu... https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch\n\n"
curl -L "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" --output /usr/local/bin/gosu
# curl "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"
# curl -L 'https://github.com/tianon/gosu/releases/download/1.14/gosu-amd64' -v --output /usr/local/bin/gosu
# curl 'https://www.sztaki.hu/sites/default/files/styles/max_650x650/public/2022/news/images/demoJAG3.jpg' --output /usr/local/bin/demoJAG3.jpg
printf  "ls -la /usr/local/bin\n\n"
ls -la /usr/local/bin
# curl "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" --output /tmp/gosu
# printf  "ls -la /tmp/gosu\n\n"
# ls -la /tmp/gosu
# curl "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" --output /usr/local/bin/gosu.asc
# wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"
# wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"
# export GNUPGHOME="$(mktemp -d)"
# gpg --batch --keyserver hkp://pool.sks-keyservers.net:80 --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4
# gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu
# rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc
chmod +x /usr/local/bin/gosu
gosu nobody true


# generate a key file for the replica set
# https://docs.mongodb.com/v3.4/tutorial/enforce-keyfile-access-control-in-existing-replica-set
printf "\n[-] Generating a replica set keyfile...\n\n"
openssl rand -base64 741 > $MONGO_KEYFILE
chown mongodb:mongodb $MONGO_KEYFILE
chmod 400 $MONGO_KEYFILE


# install Mongo
printf "\n[-] Installing MongoDB ${MONGO_VERSION}...\n\n"

# apt-key adv --keyserver hkp://pool.sks-keyservers.net:80 --recv-keys 0C49F3730359A14518585931BC711F9BA15703C6

echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/$MONGO_MAJOR main" > /etc/apt/sources.list.d/mongodb-org.list

apt-get update

apt-get install -y --force-yes \
  ${MONGO_PACKAGE}=$MONGO_VERSION \
  ${MONGO_PACKAGE}-server=$MONGO_VERSION \
  ${MONGO_PACKAGE}-shell=$MONGO_VERSION \
  ${MONGO_PACKAGE}-mongos=$MONGO_VERSION \
  ${MONGO_PACKAGE}-tools=$MONGO_VERSION


# cleanup
printf "\n[-] Cleaning up...\n\n"

rm -rf /var/lib/apt/lists/*
rm -rf /var/lib/mongodb
mv /etc/mongod.conf /etc/mongod.conf.orig

apt-get purge -y --auto-remove openssl wget
