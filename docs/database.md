# Database

## Connecting to the database

1. Run the [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy) script:

   ```bash
   ./proxy.sh ${ENVIRONMENT}
   ```

1. Obtain the database password for the environment:

   ```bash
   gcloud secrets versions access latest --project dft-schemes-${ENVIRONMENT} --secret database-password
   ```

1. Connect using PSQL and enter the password when prompted:

   ```bash
   psql -h localhost -U schemes schemes
   ```

## Creating a cold backup

To download the latest database backup for storing offline:

1. Download the backup (you will be prompted to input your BitWarden master password):

   ```bash
   ./cold-backup.sh ${ENVIRONMENT}
   ```

This will create an encrypted compressed PostgreSQL custom-format archive `schemes-${ENVIRONMENT}-${BACKUP_TIMESTAMP}.dump.gz.gpg`.

## Restoring a cold backup

To restore a backup to a local or proxied database:

1. Decrypt the archive (you will be prompted to input your BitWarden master password):

   ```bash
   bw get password "UYCS Database Backup Passphrase" \
       | ( gpg --batch --decrypt --passphrase-fd 0 --output ${ARCHIVE}.gz ${ARCHIVE}.gz.gpg && rm ${ARCHIVE}.gz.gpg )
   ```

1. Uncompress the archive:

   ```bash
   gunzip ${ARCHIVE}.gz
   ```

1. (Optional) Create a local database for the backup, if necessary:

   ```bash
   docker run -d \
       --network=host \
       -e POSTGRES_USER=schemes \
       -e POSTGRES_PASSWORD=${PGPASSWORD} \
       postgres:18
   ```

1. Restore the backup:

   ```bash
   docker run --rm -i \
       --network=host \
       -e PGUSER=schemes \
       -e PGPASSWORD=${PGPASSWORD} \
       postgres:18 \
       pg_restore -h localhost -d schemes --no-owner < ${ARCHIVE}
   ```
