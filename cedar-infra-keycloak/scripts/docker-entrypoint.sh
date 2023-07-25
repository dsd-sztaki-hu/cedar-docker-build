#!/bin/bash

export KEYCLOAK_ADMIN=${CEDAR_KEYCLOAK_ADMIN_USER}
export KEYCLOAK_ADMIN_PASSWORD=${CEDAR_KEYCLOAK_ADMIN_PASSWORD}

echo "Waiting for MySQL"

python3 -u /opt/keycloak/wait-and-init-mysql.py

echo "JAVA version ---"
echo $JAVA_HOME
java -version
echo "----------------"

dir /opt/keycloak/lib/quarkus/

/opt/keycloak/bin/kc.sh --verbose build

export INIT_DONE_FLAG="$KEYCLOAK_STATE_PATH/cedar-keycloak-init.done"
if [ ! -f ${INIT_DONE_FLAG} ]; then
  echo "Keycloak realm not yet imported!"

  echo "Creating customized realm with host $CEDAR_HOST"
  sed "s/CEDAR_HOST/$CEDAR_HOST/g" /opt/keycloak/keycloak-realm.CEDAR.development.2023-07-05.json > /opt/keycloak/keycloak-realm.CEDAR.development.2023-07-05.customized.json

  echo "Importing customized realm"
  /opt/keycloak/bin/kc.sh import --file /opt/keycloak/keycloak-realm.CEDAR.development.2023-07-05.customized.json
  /opt/keycloak/bin/kc.sh --verbose build

  echo "Creating done flag:${INIT_DONE_FLAG}"
  touch ${INIT_DONE_FLAG}
else
  echo "Keycloak realm is already imported!"
fi

/opt/keycloak/bin/kc.sh --verbose start
