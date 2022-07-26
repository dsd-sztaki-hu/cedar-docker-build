#!/bin/bash
set -e

echo "Executing sed"

sed -i 's/\.metadatacenter\.org\//\.'${CEDAR_HOST}'\//g' ${CEDAR_OPENVIEW_HOME}/index.html

# Make sure it loads the latest version  of the js
# https://github.com/metadatacenter/cedar-openview-dist/issues/1#issuecomment-1141429105
sed -i 's#\(/cedar-form/cedar-form-\)\(.*[^.]\)\.js#\1'${CEDAR_VERSION}'.js#g' ${CEDAR_OPENVIEW_HOME}/index.html

sed -i 's/\.metadatacenter\.org\//\.'${CEDAR_HOST}'\//g' ${CEDAR_OPENVIEW_HOME}/assets/data/appConfig.json


exec "$@"
