#!/bin/bash

set -e -o pipefail

if [ $# -ne 1 ]
then
	echo "Usage: cold-backup.sh <environment>"
	exit 1
fi

ENVIRONMENT=$1

PROJECT=dft-schemes-${ENVIRONMENT}
REGION=europe-west1
BACKUP_INSTANCE=schemes
RESTORE_INSTANCE=${BACKUP_INSTANCE}-restore
PGDATABASE=schemes
PGUSER=schemes

# Create Cloud SQL instance for restore

gcloud sql instances create ${RESTORE_INSTANCE} \
	--project ${PROJECT} \
	--region ${REGION} \
	--database-version POSTGRES_16 \
	--tier db-custom-1-3840 \
	--edition enterprise

# Obtain latest backup details

BACKUP=$(gcloud sql backups list \
	--project ${PROJECT} \
	--instance ${BACKUP_INSTANCE} \
	--sort-by "~enqueuedTime" \
	--limit 1 \
	--format="value(id,enqueuedTime)"
)
BACKUP_ID=$(echo "${BACKUP}" | cut -f1)
BACKUP_TIMESTAMP=$(echo "${BACKUP}" | cut -f2)
ARCHIVE=${PGDATABASE}-${ENVIRONMENT}-$(date -d $BACKUP_TIMESTAMP -u +"%Y%m%dT%H%M%SZ").dump

# Restore latest backup to restore instance

gcloud sql backups restore "${BACKUP_ID}" \
	--project ${PROJECT} \
	--backup-instance ${BACKUP_INSTANCE} \
	--restore-instance ${RESTORE_INSTANCE} \
	--quiet

# Start proxy to restore instance

./proxy.sh ${ENVIRONMENT} ${RESTORE_INSTANCE} &

# Get database password

PGPASSWORD=$(gcloud secrets versions access latest \
	--project ${PROJECT} \
	--secret database-password)

# Dump database

# Redirect output within container to avoid pg_dump truncation bug
docker run --rm \
	--network=host \
	-e PGHOST=localhost \
	-e PGUSER=${PGUSER} \
	-e PGPASSWORD=${PGPASSWORD} \
	-e PGDATABASE=${PGDATABASE} \
	-v ${PWD}:/data \
	-u "$(id -u):$(id -g)" \
	postgres:16 \
	sh -c "until pg_isready; do sleep 1; done && pg_dump --format custom --no-acl > /data/${ARCHIVE}"

# Compress archive

gzip ${ARCHIVE}

# Encrypt archive

bw get password "UYCS Database Backup Passphrase" \
	| ( gpg --batch --symmetric --passphrase-fd 0 ${ARCHIVE}.gz && rm ${ARCHIVE}.gz )

# Stop proxy to restore instance

docker stop cloud-sql-proxy

# Delete restore instance

gcloud sql instances delete \
	--project ${PROJECT} \
	--quiet \
	${RESTORE_INSTANCE}
