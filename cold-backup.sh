#!/bin/bash

set -e

if [ $# -ne 1 ]
then
    echo "Usage: cold-backup.sh <environment>"
    exit 1
fi

ENVIRONMENT=$1

PROJECT=dft-schemes-${ENVIRONMENT}
REGION=europe-west1
BACKUP_INSTANCE=schemes
RESTORE_INSTANCE=${BACKUP_INSTANCE}-backup
PGDATABASE=schemes
PGUSER=schemes
ARCHIVE=${PGDATABASE}-${ENVIRONMENT}.dump

# Create Cloud SQL instance for backup

gcloud sql instances create ${RESTORE_INSTANCE} \
	--project ${PROJECT} \
	--region ${REGION} \
	--database-version POSTGRES_16 \
	--tier db-custom-1-3840 \
	--edition enterprise

# Obtain latest backup id

BACKUP_ID=$(gcloud sql backups list \
	--project ${PROJECT} \
	--instance ${BACKUP_INSTANCE} \
	--sort-by "~windowStartTime" \
	--limit 1 \
	--format="value(id)"
)

# Restore latest backup to Cloud SQL instance

gcloud sql backups restore "${BACKUP_ID}" \
	--project ${PROJECT} \
	--backup-instance ${BACKUP_INSTANCE} \
	--restore-instance ${RESTORE_INSTANCE} \
	--quiet

# Start Cloud SQL Auth proxy

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

# Stop Cloud SQL Auth proxy

docker stop cloud-sql-proxy

# Delete Cloud SQL instance for backup

gcloud sql instances delete \
	--project ${PROJECT} \
	--quiet \
	${RESTORE_INSTANCE}
