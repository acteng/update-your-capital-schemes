#!/bin/bash

set -e

if [ $# -ne 1 ]
then
    echo "Usage: proxy.sh <environment>"
    exit 1
fi

ENVIRONMENT=$1

PROJECT=dft-schemes-${ENVIRONMENT}
DATABASE=schemes
PRIVATE_KEY_SECRET=database-private-key

INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe \
	--format="value(connectionName)" \
	--project ${PROJECT} \
	${DATABASE})

PRIVATE_KEY=$(gcloud secrets versions access latest \
	--project ${PROJECT} \
	--secret ${PRIVATE_KEY_SECRET} \
	| base64 -d)

docker run --rm \
	-p 127.0.0.1:5432:5432 \
	gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.9.0 \
	--address 0.0.0.0 \
	--port 5432 \
	--json-credentials "${PRIVATE_KEY}" \
	${INSTANCE_CONNECTION_NAME}
