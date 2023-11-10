#!/bin/bash
#
# Entrypoint to import our config and then start the container as usual
#

# Path to your realm JSON file inside the container
REALM_JSON="/config/my-realm-config.json"

# Import the realm config if it hasn't been imported yet
/opt/bitnami/keycloak/bin/kc.sh import --file $REALM_JSON

# Call the original entrypoint script to start Keycloak
exec /opt/bitnami/scripts/keycloak/entrypoint.sh "$@"
