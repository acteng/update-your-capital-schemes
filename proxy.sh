#!/bin/bash

set -e

if [ $# -lt 1 ]
then
    echo "Usage: proxy.sh <environment> <instance>"
    exit 1
fi

ENVIRONMENT=$1
INSTANCE=${2:-schemes}

PROJECT=dft-schemes-${ENVIRONMENT}
PRIVATE_KEY_SECRET=database-private-key

INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe \
	--format="value(connectionName)" \
	--project ${PROJECT} \
	${INSTANCE})

PRIVATE_KEY=$(gcloud secrets versions access latest \
	--project ${PROJECT} \
	--secret ${PRIVATE_KEY_SECRET} \
	| base64 -d)

docker run --rm \
	--name cloud-sql-proxy \
	-p 127.0.0.1:5432:5432 \
	gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.11.4 \
	--address 0.0.0.0 \
	--port 5432 \
	--json-credentials "${PRIVATE_KEY}" \
	${INSTANCE_CONNECTION_NAME}
